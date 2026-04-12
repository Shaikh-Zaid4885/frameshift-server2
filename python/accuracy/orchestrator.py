"""
Accuracy Improvers Orchestrator
Coordinates all accuracy improvers for comprehensive Django→Flask conversion
"""

import sys
import os
from typing import Dict, List, Optional, Tuple

# Import all accuracy improvers
from .model_accuracy_improver import ModelAccuracyImprover
from .routes_accuracy_improver import RoutesAccuracyImprover
from .templates_accuracy_improver import TemplatesAccuracyImprover
from .urls_accuracy_improver import URLPatternAccuracyImprover
from .forms_queries_accuracy_improver import FormsQueriesAccuracyImprover


class AccuracyImprovementsOrchestrator:
    """
    Coordinates all accuracy improvements for Django→Flask conversion
    Applies improvements to each component type and tracks overall accuracy
    """

    def __init__(self):
        self.model_improver = ModelAccuracyImprover()
        self.routes_improver = RoutesAccuracyImprover()
        self.templates_improver = TemplatesAccuracyImprover()
        self.urls_improver = URLPatternAccuracyImprover()
        self.forms_improver = FormsQueriesAccuracyImprover()
        
        self.improvement_results = {
            'models': {},
            'routes': {},
            'templates': {},
            'urls': {},
            'forms': {},
            'queries': {},
        }

    def improve_models(self, original: str, converted: str) -> Tuple[str, Dict]:
        """
        Apply model accuracy improvements
        """
        improved = converted
        
        # Apply all improvements
        improved = self.model_improver.improve_field_conversion(improved)
        improved = self.model_improver.improve_relationship_conversion(improved)
        improved = self.model_improver.improve_model_inheritance(improved)
        improved = self.model_improver.improve_meta_options(improved)
        
        # Add imports
        improved = self.model_improver.add_missing_imports(improved)
        
        # Validate
        validation = self.model_improver.validate_conversion(original, improved)
        
        self.improvement_results['models'] = validation
        
        return improved, validation

    def improve_routes(self, original: str, converted: str) -> Tuple[str, Dict]:
        """
        Apply route accuracy improvements
        """
        improved = converted
        
        # Apply improvements for function-based views
        improved = self.routes_improver.improve_function_based_views(improved)
        
        # Apply improvements for class-based views
        improved = self.routes_improver.improve_class_based_views(improved)
        
        # Improve form handling
        improved = self.routes_improver.improve_form_handling(improved)
        
        # Improve database queries in views
        improved = self.routes_improver.improve_database_queries(improved)
        
        # Improve authentication
        improved = self.routes_improver.improve_authentication(improved)
        
        # Add imports
        improved = self.routes_improver.add_missing_imports(improved)
        
        # Validate
        validation = self.routes_improver.validate_conversion(original, improved)
        
        self.improvement_results['routes'] = validation
        
        return improved, validation

    def improve_templates(self, original: str, converted: str) -> Tuple[str, Dict]:
        """
        Apply template accuracy improvements
        """
        improved = converted
        
        # Apply improvements
        improved = self.templates_improver.improve_template_tags(improved)
        improved = self.templates_improver.improve_block_tags(improved)
        improved = self.templates_improver.improve_template_filters(improved)
        improved = self.templates_improver.improve_static_files(improved)
        improved = self.templates_improver.improve_form_rendering(improved)
        improved = self.templates_improver.improve_url_references(improved)
        improved = self.templates_improver.improve_template_variables(improved)
        improved = self.templates_improver.improve_conditional_expressions(improved)
        improved = self.templates_improver.add_template_macros(improved)
        improved = self.templates_improver.improve_inheritance_chain(improved)
        
        # Validate
        validation = self.templates_improver.validate_conversion(original, improved)
        
        self.improvement_results['templates'] = validation
        
        return improved, validation

    def improve_urls(self, original: str, converted: str, view_code: str = "") -> Tuple[str, str, Dict]:
        """
        Apply URL pattern accuracy improvements
        Returns: improved URLs, improved views, validation
        """
        improved_urls = converted
        improved_views = view_code
        
        # Apply improvements
        improved_urls = self.urls_improver.improve_path_patterns(improved_urls)
        improved_urls = self.urls_improver.improve_re_path_patterns(improved_urls)
        improved_urls = self.urls_improver.improve_url_includes(improved_urls)
        improved_urls = self.urls_improver.improve_trailing_slashes(improved_urls)
        
        # Convert named URLs in views
        improved_urls, improved_views = self.urls_improver.improve_named_urls(
            improved_urls, improved_views
        )
        
        # Add helpers
        improved_views = self.urls_improver.add_url_building_helpers(improved_views)
        improved_urls = self.urls_improver.add_error_handlers(improved_urls)
        improved_urls = self.urls_improver.add_api_route_versioning(improved_urls)
        
        # Validate
        validation = self.urls_improver.validate_conversion(original, improved_urls)
        
        self.improvement_results['urls'] = validation
        
        return improved_urls, improved_views, validation

    def improve_forms_and_queries(self, original: str, converted: str) -> Tuple[str, Dict]:
        """
        Apply form and query accuracy improvements
        """
        improved = converted
        
        # Apply form improvements
        improved = self.forms_improver.improve_form_fields(improved)
        improved = self.forms_improver.improve_form_validation(improved)
        improved = self.forms_improver.improve_model_choices(improved)
        
        # Apply query improvements
        improved = self.forms_improver.improve_database_queries(improved)
        improved = self.forms_improver.improve_query_filters(improved)
        improved = self.forms_improver.improve_query_aggregation(improved)
        improved = self.forms_improver.improve_query_joins(improved)
        improved = self.forms_improver.add_session_management(improved)
        
        # Add imports
        improved = self.forms_improver.add_imports(improved)
        
        # Validate
        validation = self.forms_improver.validate_conversion(original, improved)
        
        self.improvement_results['forms'] = validation
        
        return improved, validation

    def calculate_overall_accuracy(self) -> Dict:
        """
        Calculate overall conversion accuracy based on all components
        """
        if not self.improvement_results:
            return {'overall_score': 0, 'components': {}}
        
        scores = []
        component_scores = {}
        
        for component, result in self.improvement_results.items():
            if 'accuracy_score' in result:
                score = result['accuracy_score']
                scores.append(score)
                component_scores[component] = score
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': round(overall_score, 2),
            'components': component_scores,
            'details': self.improvement_results
        }

    def generate_accuracy_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive accuracy improvement report
        """
        report = []
        report.append("=" * 80)
        report.append("DJANGO-TO-FLASK CONVERSION ACCURACY REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Component-wise accuracy
        report.append("COMPONENT-WISE ACCURACY SCORES:")
        report.append("-" * 80)
        
        for component, result in self.improvement_results.items():
            score = result.get('accuracy_score', 0)
            is_valid = result.get('is_valid', False)
            issues = result.get('issues', [])
            
            status = "✓ VALID" if is_valid else "⚠ NEEDS REVIEW"
            report.append(f"\n{component.upper()}: {score}% {status}")
            
            if issues:
                report.append("  Issues found:")
                for issue in issues:
                    report.append(f"    - {issue}")
            
            # Additional info by component
            if component == 'models' and 'model_count' in result:
                report.append(f"  Models converted: {result['model_count']}")
            elif component == 'routes' and 'view_count' in result:
                report.append(f"  Views converted: {result['view_count']}")
            elif component == 'templates' and 'template_tags' in result:
                report.append(f"  Template tags: {result['template_tags']}")
            elif component == 'urls' and 'route_count' in result:
                report.append(f"  Routes generated: {result['route_count']}")
            elif component == 'forms' and 'field_count' in result:
                report.append(f"  Form fields: {result['field_count']}")
                report.append(f"  Queries: {result.get('query_count', 0)}")
        
        # Overall accuracy
        overall = self.calculate_overall_accuracy()
        report.append("\n" + "=" * 80)
        report.append(f"OVERALL ACCURACY SCORE: {overall['overall_score']}%")
        report.append("=" * 80)
        
        # Summary
        report.append("\nSUMMARY:")
        report.append("-" * 80)
        
        total_valid = sum(1 for r in self.improvement_results.values() if r.get('is_valid', False))
        total_components = len(self.improvement_results)
        
        report.append(f"✓ Components Valid: {total_valid}/{total_components}")
        
        total_issues = sum(len(r.get('issues', [])) for r in self.improvement_results.values())
        report.append(f"⚠ Total Issues Found: {total_issues}")
        
        if overall['overall_score'] >= 90:
            report.append("\n✓ Conversion Quality: EXCELLENT (90%+)")
            report.append("  Flask application should function correctly")
        elif overall['overall_score'] >= 80:
            report.append("\n✓ Conversion Quality: GOOD (80-89%)")
            report.append("  Flask application should function with minor adjustments")
        elif overall['overall_score'] >= 70:
            report.append("\n⚠ Conversion Quality: FAIR (70-79%)")
            report.append("  Flask application needs some manual review and fixes")
        else:
            report.append("\n✗ Conversion Quality: POOR (<70%)")
            report.append("  Flask application needs significant manual work")
        
        report.append("\n" + "=" * 80)
        
        report_text = "\n".join(report)
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text

    def print_accuracy_report(self):
        """Print accuracy report to console"""
        report = self.generate_accuracy_report()
        print(report)

    def get_improvement_recommendations(self) -> List[str]:
        """
        Get list of recommendations for further improvement
        """
        recommendations = []
        
        for component, result in self.improvement_results.items():
            if not result.get('is_valid', False):
                issues = result.get('issues', [])
                if issues:
                    recommendations.append(f"• {component.upper()}: {issues[0]}")
        
        if not recommendations:
            recommendations.append("• All components have acceptable accuracy")
            recommendations.append("• Run full integration tests to validate converted application")
            recommendations.append("• Compare Flask behavior with original Django application")
        
        return recommendations


def orchestrate_conversion_improvements(
    django_files: Dict[str, str],
    flask_files: Dict[str, str]
) -> Dict:
    """
    Main orchestration function for all accuracy improvements
    
    Args:
        django_files: Dict of {file_type: original_content}
            Expected keys: 'models', 'views', 'templates', 'urls', 'forms'
        flask_files: Dict of {file_type: converted_content}
    
    Returns:
        Dict with improved content and accuracy scores
    """
    orchestrator = AccuracyImprovementsOrchestrator()
    results = {
        'improved_files': {},
        'accuracy_scores': {},
        'overall_accuracy': 0,
    }
    
    # Improve models
    if 'models' in django_files and 'models' in flask_files:
        improved, validation = orchestrator.improve_models(
            django_files['models'],
            flask_files['models']
        )
        results['improved_files']['models'] = improved
        results['accuracy_scores']['models'] = validation
    
    # Improve routes/views
    if 'views' in django_files and 'views' in flask_files:
        improved, validation = orchestrator.improve_routes(
            django_files['views'],
            flask_files['views']
        )
        results['improved_files']['views'] = improved
        results['accuracy_scores']['views'] = validation
    
    # Improve templates
    if 'templates' in django_files and 'templates' in flask_files:
        improved, validation = orchestrator.improve_templates(
            django_files['templates'],
            flask_files['templates']
        )
        results['improved_files']['templates'] = improved
        results['accuracy_scores']['templates'] = validation
    
    # Improve URLs
    if 'urls' in django_files and 'urls' in flask_files:
        view_code = flask_files.get('views', '')
        improved_urls, improved_views, validation = orchestrator.improve_urls(
            django_files['urls'],
            flask_files['urls'],
            view_code
        )
        results['improved_files']['urls'] = improved_urls
        results['improved_files']['views'] = improved_views  # Update with improved views
        results['accuracy_scores']['urls'] = validation
    
    # Improve forms and queries
    if 'forms' in django_files and 'forms' in flask_files:
        improved, validation = orchestrator.improve_forms_and_queries(
            django_files['forms'],
            flask_files['forms']
        )
        results['improved_files']['forms'] = improved
        results['accuracy_scores']['forms'] = validation
    
    # Calculate overall accuracy
    overall = orchestrator.calculate_overall_accuracy()
    results['overall_accuracy'] = overall['overall_score']
    
    # Generate report
    report = orchestrator.generate_accuracy_report()
    results['report'] = report
    
    return results
