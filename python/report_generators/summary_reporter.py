from typing import Dict
from ..utils.logger import logger


class SummaryReporter:
    """Generate summary report for conversion"""

    def generate(self, conversion_results: Dict) -> Dict:
        """
        Generate comprehensive conversion report

        Args:
            conversion_results: Dictionary containing all conversion results

        Returns:
            Summary report dictionary
        """
        logger.info("Generating conversion summary report")

        # Extract results from each converter
        analysis = conversion_results.get('analysis', {})
        models = conversion_results.get('models', {})
        views = conversion_results.get('views', {})
        urls = conversion_results.get('urls', {})
        templates = conversion_results.get('templates', {})
        verification = conversion_results.get('verification', {})
        ai_enhancements = conversion_results.get('ai_enhancements', {})

        # Calculate overall accuracy
        accuracy_score = self._calculate_accuracy(
            models,
            views,
            urls,
            templates,
            verification,
            ai_enhancements
        )

        # Compile all issues
        all_issues = []
        all_issues.extend(models.get('issues', []))
        all_issues.extend(views.get('issues', []))
        all_issues.extend(urls.get('issues', []))
        all_issues.extend(templates.get('issues', []))

        # Compile all warnings
        all_warnings = []
        all_warnings.extend(models.get('warnings', []))
        all_warnings.extend(views.get('warnings', []))
        all_warnings.extend(urls.get('warnings', []))
        all_warnings.extend(templates.get('warnings', []))

        # Collect manual change indicators from converter warnings/issues
        manual_indicators = self._collect_manual_change_indicators(
            models, views, urls, templates
        )

        # Generate summary
        report = {
            'success': True,
            'accuracy_score': accuracy_score,
            'total_files_converted': (
                len(models.get('converted_files', []) or models.get('files_converted', [])) +
                len(views.get('converted_files', []) or views.get('converted_routes', [])) +
                len(urls.get('converted_files', [])) +
                len(templates.get('converted_files', []))
            ),
            'models_converted': models.get('total_models', 0),
            'views_converted': views.get('total_views', 0),
            'urls_converted': urls.get('total_patterns', 0),
            'templates_converted': templates.get('total_templates', 0),
            'issues': all_issues,
            'warnings': all_warnings,
            'suggestions': self._generate_suggestions(analysis, models, views, urls),
            'gemini_verification': verification,
            'summary': self._generate_summary_text(analysis, accuracy_score, ai_enhancements, verification),
            'ai_enhancement': {
                'enabled': bool(ai_enhancements.get('enabled')),
                'applied_count': len(ai_enhancements.get('applied', []) or []),
                'applied': ai_enhancements.get('applied', []) or []
            },
            'manual_changes_summary': manual_indicators,
            'next_steps': self._generate_next_steps(all_issues, all_warnings, manual_indicators)
        }

        logger.info(f"Report generated with accuracy score: {accuracy_score}%")

        return report

    def _calculate_accuracy(
        self,
        models: Dict,
        views: Dict,
        urls: Dict,
        templates: Dict,
        verification: Dict,
        ai_enhancements: Dict
    ) -> float:
        """Calculate overall conversion accuracy score"""
        components = [
            self._score_component(models, 'total_models'),
            self._score_component(views, 'total_views'),
            self._score_component(urls, 'total_patterns'),
            self._score_component(templates, 'total_templates'),
        ]

        weighted_total = sum(component['weight'] for component in components)
        if weighted_total == 0:
            return 0.0

        base_score = sum(
            component['score'] * component['weight'] for component in components
        ) / weighted_total

        total_warnings = sum(len(component.get('warnings', [])) for component in [models, views, urls, templates])
        warning_penalty = min(total_warnings * 2.0, 15.0)
        score = base_score - warning_penalty

        score = self._apply_ai_adjustments(score, verification, ai_enhancements)

        return round(max(0.0, min(score, 100.0)), 2)

    def _apply_ai_adjustments(self, score: float, verification: Dict, ai_enhancements: Dict) -> float:
        """Apply AI bonuses without letting advisory AI review lower the deterministic score."""
        adjusted_score = score

        applied_enhancements = ai_enhancements.get('applied', []) or []
        if ai_enhancements.get('enabled') and applied_enhancements:
            enhancement_bonus = min(len(applied_enhancements) * 5.0, 20.0)
            adjusted_score += enhancement_bonus

        ai_summary = verification.get('ai_summary', {}) or {}
        ai_quality = ai_summary.get('overall_quality')
        if verification.get('enabled') and isinstance(ai_quality, (int, float)):
            # Gemini review is advisory and can be noisy when upstream stats are incomplete.
            # Keep deterministic validation as the floor; only let AI verification improve the score.
            blended_score = (adjusted_score * 0.7) + (float(ai_quality) * 0.3)
            adjusted_score = max(adjusted_score, blended_score)

        return adjusted_score

    def _score_component(self, component: Dict, total_key: str) -> Dict:
        total_items = component.get(total_key, 0) or 0
        converted_files = (
            component.get('converted_files', [])
            or component.get('files_converted', [])
            or component.get('converted_routes', [])
            or []
        )
        issues = component.get('issues', []) or []
        stats = component.get('stats', {}) or {}
        total_files = stats.get('total_files', 0) or 0
        failed_files = stats.get('failed', 0) or 0

        weight = max(total_items, len(converted_files), total_files, len(issues))
        if weight == 0:
            return {'score': 0.0, 'weight': 0}

        direct_accuracy = component.get('accuracy') or component.get('accuracy_score')
        if isinstance(direct_accuracy, (int, float)):
            score = float(direct_accuracy)
            failed_entries = [
                issue for issue in issues
                if issue.get('status') == 'failed'
            ]
            if issues:
                completion_ratio = max(
                    0.0,
                    1.0 - (len(failed_entries) / max(len(issues), 1))
                )
                score *= completion_ratio
            return {'score': score, 'weight': weight}

        successful_entries = [
            issue for issue in issues
            if issue.get('status') == 'converted'
        ]
        failed_entries = [
            issue for issue in issues
            if issue.get('status') == 'failed'
        ]

        if successful_entries:
            avg_confidence = sum(
                issue.get('confidence', 100.0) for issue in successful_entries
            ) / len(successful_entries)
        else:
            implementation_ratio = None
            if isinstance(component.get('fully_implemented'), (int, float)) and total_items:
                implementation_ratio = component.get('fully_implemented') / max(total_items, 1)

            if implementation_ratio is not None:
                avg_confidence = max(60.0, implementation_ratio * 100.0)
            else:
                if total_files and failed_files >= total_files and not converted_files:
                    avg_confidence = 0.0
                else:
                    avg_confidence = 100.0 if converted_files else 0.0

        if issues:
            completion_ratio = max(
                0.0,
                1.0 - (len(failed_entries) / max(len(issues), 1))
            )
        else:
            completion_ratio = max(0.0, 1.0 - (failed_files / max(total_files, 1))) if total_files else 1.0

        score = avg_confidence * completion_ratio
        return {'score': score, 'weight': weight}

    def _generate_summary_text(
        self,
        analysis: Dict,
        accuracy_score: float,
        ai_enhancements: Dict,
        verification: Dict
    ) -> str:
        """Generate human-readable summary"""

        apps_count = len(analysis.get('apps', []))
        django_version = analysis.get('django_version', 'Unknown')
        applied_enhancements = ai_enhancements.get('applied', []) or []
        ai_summary = verification.get('ai_summary', {}) or {}
        ai_quality = ai_summary.get('overall_quality')

        summary = f"""
Django to Flask Conversion Summary
=====================================

Project Analysis:
- Django Version: {django_version}
- Number of Apps: {apps_count}

Conversion Accuracy: {accuracy_score}%
AI Enhancement Enabled: {'Yes' if ai_enhancements.get('enabled') else 'No'}
AI Enhancements Applied: {len(applied_enhancements)}
AI Verification Quality: {f"{ai_quality}%" if isinstance(ai_quality, (int, float)) else 'Not available'}

The conversion process has been completed. Please review the generated Flask
application and address any warnings or issues before deployment.

Key areas requiring manual review:
1. Database relationships (ForeignKey, ManyToMany)
2. Custom template tags and filters
3. Django-specific middleware
4. Authentication and permissions
5. Form validation

All converted files maintain the original structure for easy comparison.
        """

        return summary.strip()

    def _generate_suggestions(self, analysis: Dict, models: Dict, views: Dict, urls: Dict) -> list:
        """Generate suggestions for improvement"""

        suggestions = []

        # Models suggestions
        if models.get('total_models', 0) > 0:
            suggestions.append({
                'category': 'models',
                'message': 'Install Flask-SQLAlchemy and initialize db instance in your Flask app',
                'code': 'pip install flask-sqlalchemy'
            })

        # Views suggestions
        if views.get('total_views', 0) > 0:
            suggestions.append({
                'category': 'views',
                'message': 'Add route decorators to converted view functions',
                'code': '@app.route("/path") or @bp.route("/path")'
            })

        # URLs suggestions
        if urls.get('total_patterns', 0) > 0:
            suggestions.append({
                'category': 'urls',
                'message': 'Integrate converted routes with Flask blueprints',
                'code': 'app.register_blueprint(bp)'
            })

        # Authentication suggestion
        suggestions.append({
            'category': 'authentication',
            'message': 'Install Flask-Login for user authentication',
            'code': 'pip install flask-login'
        })

        return suggestions

    def _collect_manual_change_indicators(self, models, views, urls, templates):
        """Collect indicators of manual changes required from converter results.

        This aggregates file-level information about Django patterns that the
        converters flagged as needing manual review.  The line-level detail is
        produced later by the Node.js DiffService and attached to file_diffs.
        """
        indicators = []
        manual_keywords = {'manual', 'todo', 'requires', 'need'}

        for component_name, component in [
            ('models', models),
            ('views', views),
            ('urls', urls),
            ('templates', templates),
        ]:
            for issue in component.get('issues', []):
                msg = (issue.get('message', '') or '').lower()
                if any(kw in msg for kw in manual_keywords):
                    indicators.append({
                        'file': issue.get('file') or issue.get('filename') or 'Unknown',
                        'category': component_name,
                        'message': issue.get('message', ''),
                        'severity': issue.get('severity', 'warning'),
                    })

            for warning in component.get('warnings', []):
                if isinstance(warning, dict):
                    msg = (warning.get('message', '') or '').lower()
                else:
                    msg = str(warning).lower()

                if any(kw in msg for kw in manual_keywords):
                    w_message = warning.get('message', str(warning)) if isinstance(warning, dict) else str(warning)
                    indicators.append({
                        'file': warning.get('file', 'project-wide') if isinstance(warning, dict) else 'project-wide',
                        'category': component_name,
                        'message': w_message,
                        'severity': 'warning',
                    })

        return {
            'total_items': len(indicators),
            'items': indicators,
        }

    def _generate_next_steps(self, issues: list, warnings: list, manual_indicators=None) -> list:
        """Generate next steps for the developer"""

        steps = []
        step_num = 1

        steps.append(f"{step_num}. Review all converted files for accuracy")
        step_num += 1
        steps.append(f"{step_num}. Install required Flask dependencies (see suggestions)")
        step_num += 1
        steps.append(f"{step_num}. Initialize Flask app and database")
        step_num += 1
        steps.append(f"{step_num}. Register blueprints for each converted app")
        step_num += 1

        manual_count = (manual_indicators or {}).get('total_items', 0)
        if manual_count > 0:
            steps.append(
                f"{step_num}. ⚠ Address {manual_count} manual change(s) flagged in the report "
                f"(check the 'Manual Changes Required' section for file names and line numbers)"
            )
            step_num += 1

        if issues:
            steps.append(f"{step_num}. Fix {len(issues)} conversion issues")
            step_num += 1

        if warnings:
            steps.append(f"{step_num}. Address {len(warnings)} warnings")
            step_num += 1

        steps.append(f"{step_num}. Run tests to verify functionality")
        step_num += 1
        steps.append(f"{step_num}. Update requirements.txt with Flask dependencies")

        return steps


__all__ = ['SummaryReporter']
