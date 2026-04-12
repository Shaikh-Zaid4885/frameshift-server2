#!/usr/bin/env python3
"""
FrameShift Python Conversion Engine
Main entry point for Django-to-Flask conversion
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.analyzers.django_analyzer import DjangoAnalyzer
from python.analyzers.framework_detector import FrameworkDetector
from python.converters.ast_models_converter import HybridModelsConverter
from python.converters.ast_routes_converter import ASTRoutesConverter
from python.converters.static_copier import StaticCopier
from python.converters.templates_converter import TemplatesConverter
from python.converters.urls_converter import URLsConverter
from python.converters.settings_converter import SettingsConverter
from python.converters.forms_converter import FormsConverter
from python.converters.admin_converter import AdminConverter
from python.converters.signals_converter import SignalsConverter
from python.converters.middleware_converter import MiddlewareConverter
from python.generators.smart_flask_generator import SmartFlaskGenerator
from python.report_generators.summary_reporter import SummaryReporter
from python.services.ai_enhancer import AIEnhancer
from python.services.gemini_verifier import GeminiVerifier
from python.services.ai_project_enhancer import AIProjectEnhancer
from python.accuracy.orchestrator import AccuracyImprovementsOrchestrator
from python.utils.logger import logger
from python.utils.progress_emitter import ProgressEmitter


def emit_progress(job_id, step, progress, message):
    """Emit progress update to Node.js."""
    ProgressEmitter.emit(job_id, step, progress, message)


def normalize_conversion_mode(raw_mode):
    mode = (raw_mode or 'default').strip().lower()
    return mode if mode in ['default', 'custom'] else 'default'


def resolve_ai_provider_config(args, conversion_mode):
    if conversion_mode == 'custom':
        return {
            'provider': os.getenv('CUSTOM_API_PROVIDER'),
            'api_key': os.getenv('CUSTOM_API_KEY'),
            'endpoint': os.getenv('CUSTOM_API_ENDPOINT') or None,
            'model': os.getenv('CUSTOM_API_MODEL') or None
        }

    return {
        'provider': 'gemini',
        'api_key': args.gemini_api_key,
        'endpoint': None,
        'model': None
    }


def main():
    """Main conversion function."""
    parser = argparse.ArgumentParser(description='Convert Django project to Flask')
    parser.add_argument('--job-id', required=True, help='Conversion job ID')
    parser.add_argument('--project-path', required=True, help='Path to Django project')
    parser.add_argument('--output-path', required=True, help='Output path for Flask project')
    parser.add_argument('--gemini-api-key', help='Google Gemini API key for verification')
    parser.add_argument('--use-ai', default='true', help='Use AI enhancement (true/false)')
    parser.add_argument('--conversion-mode', default='default', help='Conversion mode: default or custom')
    args = parser.parse_args()

    use_ai = args.use_ai.lower() == 'true'
    conversion_mode = normalize_conversion_mode(args.conversion_mode)

    try:
        logger.info(f"Starting conversion for job {args.job_id}")
        logger.info(f"Django project: {args.project_path}")
        logger.info(f"Output path: {args.output_path}")
        logger.info(f"AI Enhancement: {'Enabled' if use_ai else 'Disabled'}")
        logger.info(f"Conversion mode: {conversion_mode}")

        emit_progress(args.job_id, 'detecting_framework', 5, 'Detecting project framework')
        detector = FrameworkDetector(args.project_path)
        framework_result = detector.detect()

        if not framework_result['is_supported']:
            error_msg = f"Unsupported framework: {framework_result['framework']}. Only Django projects are currently supported."
            logger.error(error_msg)
            raise ValueError(error_msg)

        emit_progress(args.job_id, 'analyzing', 10, 'Analyzing Django project structure')
        analyzer = DjangoAnalyzer(args.project_path)
        analysis_result = analyzer.analyze()
        analysis_result['framework_detection'] = framework_result

        emit_progress(args.job_id, 'converting_models', 20, 'Converting Django models (20%)')
        hybrid_models_converter = HybridModelsConverter(args.project_path, args.output_path)
        models_result = hybrid_models_converter.convert()

        emit_progress(args.job_id, 'converting_views', 35, 'Converting views to Flask routes (35%)')
        ast_routes_converter = ASTRoutesConverter(args.project_path, args.output_path)
        views_result = ast_routes_converter.convert()

        emit_progress(args.job_id, 'converting_urls', 45, 'Converting URL patterns (45%)')
        urls_converter = URLsConverter(args.project_path, args.output_path)
        urls_result = urls_converter.convert()

        emit_progress(args.job_id, 'converting_settings', 50, 'Converting settings and config (50%)')
        settings_converter = SettingsConverter(args.project_path, args.output_path)
        settings_result = settings_converter.convert()

        emit_progress(args.job_id, 'converting_forms', 55, 'Converting forms (55%)')
        forms_converter = FormsConverter(args.project_path, args.output_path)
        forms_result = forms_converter.convert()

        emit_progress(args.job_id, 'converting_admin', 60, 'Converting admin (60%)')
        admin_converter = AdminConverter(args.project_path, args.output_path)
        admin_result = admin_converter.convert()

        emit_progress(args.job_id, 'converting_signals', 65, 'Converting signals (65%)')
        signals_converter = SignalsConverter(args.project_path, args.output_path)
        signals_result = signals_converter.convert()

        emit_progress(args.job_id, 'converting_middleware', 70, 'Converting middleware (70%)')
        mw_converter = MiddlewareConverter(args.project_path, args.output_path)
        mw_result = mw_converter.convert()

        project_path = Path(args.project_path)
        subdirs = [d for d in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, d))]
        project_name = subdirs[0] if subdirs else project_path.name
        flask_project_path = Path(args.output_path) / project_name

        emit_progress(args.job_id, 'converting_templates', 75, 'Converting templates (75%)')
        templates_converter = TemplatesConverter(args.project_path, str(flask_project_path))
        templates_result = templates_converter.convert()

        emit_progress(args.job_id, 'copying_static', 80, 'Copying static files (80%)')
        static_copier = StaticCopier(args.project_path, str(flask_project_path))
        static_result = static_copier.copy()
        logger.info(f"Static files copied: {static_result.get('total_static_files', 0)}")

        emit_progress(args.job_id, 'generating_skeleton', 83, 'Generating runnable Flask application')
        flask_generator = SmartFlaskGenerator(str(flask_project_path), project_name)
        flask_result = flask_generator.generate_all()
        logger.info(f"Generated Flask app files: {len(flask_result.get('files_generated', []))}")

        # Resolve AI provider configuration early so it is available for all
        # AI-related steps below (comprehensive enhancement, per-file enhancement,
        # and verification).
        ai_config = resolve_ai_provider_config(args, conversion_mode)

        # NEW: Apply accuracy improvements to all components
        emit_progress(args.job_id, 'improving_accuracy', 85, 'Applying accuracy improvements to conversion')
        try:
            accuracy_orchestrator = AccuracyImprovementsOrchestrator()
            
            # Improve models
            if models_result.get('converted_content'):
                improved_models, model_validation = accuracy_orchestrator.improve_models(
                    analysis_result.get('models_content', ''),
                    models_result.get('converted_content', '')
                )
                models_result['converted_content'] = improved_models
                models_result['accuracy_score'] = model_validation.get('accuracy_score', 0)
                logger.info(f"Models accuracy score: {model_validation.get('accuracy_score', 0)}%")
            
            # Improve routes
            if views_result.get('converted_content'):
                improved_views, routes_validation = accuracy_orchestrator.improve_routes(
                    analysis_result.get('views_content', ''),
                    views_result.get('converted_content', '')
                )
                views_result['converted_content'] = improved_views
                views_result['accuracy_score'] = routes_validation.get('accuracy_score', 0)
                logger.info(f"Routes accuracy score: {routes_validation.get('accuracy_score', 0)}%")
            
            # Improve templates
            if templates_result.get('converted_content'):
                improved_templates, templates_validation = accuracy_orchestrator.improve_templates(
                    analysis_result.get('templates_content', ''),
                    templates_result.get('converted_content', '')
                )
                templates_result['converted_content'] = improved_templates
                templates_result['accuracy_score'] = templates_validation.get('accuracy_score', 0)
                logger.info(f"Templates accuracy score: {templates_validation.get('accuracy_score', 0)}%")
            
            # Improve URLs — pass (url_content, view_content, view_code) per signature
            improved_urls, improved_views, urls_validation = accuracy_orchestrator.improve_urls(
                urls_result.get('converted_content', ''),
                views_result.get('converted_content', ''),
                views_result.get('converted_content', '')
            )
            urls_result['converted_content'] = improved_urls
            views_result['converted_content'] = improved_views
            urls_result['accuracy_score'] = urls_validation.get('accuracy_score', 0)
            logger.info(f"URLs accuracy score: {urls_validation.get('accuracy_score', 0)}%")
            
            # Improve forms and queries
            if views_result.get('converted_content'):
                improved_forms, forms_validation = accuracy_orchestrator.improve_forms_and_queries(
                    analysis_result.get('forms_content', ''),
                    views_result.get('converted_content', '')
                )
                views_result['converted_content'] = improved_forms
                views_result['accuracy_score'] = max(
                    views_result.get('accuracy_score', 0),
                    forms_validation.get('accuracy_score', 0)
                )
                logger.info(f"Forms/Queries accuracy score: {forms_validation.get('accuracy_score', 0)}%")
            
            # Write accuracy-improved content back to disk so improvements
            # are reflected in the actual converted project files.
            _write_improved_content_to_disk(
                flask_project_path, models_result, views_result,
                urls_result, templates_result, logger
            )
            
        except Exception as e:
            logger.warning(f"Accuracy improvement phase failed (non-fatal): {str(e)}")
            # Continue with conversion even if accuracy improvements fail

        # NEW: Comprehensive AI enhancement of all files
        emit_progress(args.job_id, 'ai_full_enhancement', 86, 'Applying comprehensive AI enhancement to all files')
        if use_ai and ai_config['api_key']:
            try:
                logger.info(f"Starting comprehensive AI enhancement of all project files")
                
                project_enhancer = AIProjectEnhancer(
                    api_key=ai_config['api_key'],
                    provider=ai_config['provider'],
                    model=ai_config['model']
                )
                
                # Enhance all Python files in the project
                def enhancement_progress(p, msg):
                    # Map 0-100% of enhancement to 86-89% total progress
                    total_p = 86 + int((p / 100) * 3)
                    emit_progress(args.job_id, 'ai_full_enhancement', total_p, msg)
                
                enhancement_results = project_enhancer.enhance_all_files(
                    str(flask_project_path), 
                    progress_callback=enhancement_progress
                )
                
                logger.info(f"AI Enhancement completed:")
                logger.info(f"  Total files: {enhancement_results['total_files']}")
                logger.info(f"  Files enhanced: {enhancement_results['files_enhanced']}")
                logger.info(f"  Average accuracy: {enhancement_results['average_accuracy']}%")
                
                # Save enhanced files
                project_enhancer.save_enhanced_files(enhancement_results, str(flask_project_path))
                
                # Generate enhancement report
                enhancement_report = project_enhancer.generate_enhancement_report(enhancement_results)
                logger.info(f"Enhancement report:\n{enhancement_report}")
                
                # Validate enhanced Flask app
                validation_results = project_enhancer.validate_flask_app(str(flask_project_path))
                logger.info(f"Flask app validation: {validation_results}")
                
                # Emit enhancement results
                ProgressEmitter.emit_custom(args.job_id, 'ai_enhancement_results', {
                    'total_files': enhancement_results['total_files'],
                    'files_enhanced': enhancement_results['files_enhanced'],
                    'average_accuracy': enhancement_results['average_accuracy'],
                    'report': enhancement_report,
                    'validation': validation_results
                })
                
            except Exception as e:
                logger.warning(f"Comprehensive AI enhancement failed (non-fatal): {str(e)}")
                # Continue with conversion even if enhancement fails

        # Legacy AI enhancement is now replaced by comprehensive AIProjectEnhancer
        ai_enhancements = {
            'enabled': use_ai and bool(ai_config['api_key']),
            'applied': enhancement_results.get('improvements_made', []) if 'enhancement_results' in locals() else []
        }

        # Update high-fidelity scores if AI was used
        if 'enhancement_results' in locals() and enhancement_results.get('files_enhanced', 0) > 0:
            logger.info("Synchronizing AI enhancement scores for final report")
            avg_ai_score = enhancement_results.get('average_accuracy', 0)
            
            # Update component scores if AI score is higher (High Fidelity)
            if models_result:
                models_result['accuracy_score'] = max(models_result.get('accuracy_score', 0), avg_ai_score)
            if views_result:
                views_result['accuracy_score'] = max(views_result.get('accuracy_score', 0), avg_ai_score)
            if urls_result:
                urls_result['accuracy_score'] = max(urls_result.get('accuracy_score', 0), avg_ai_score)
            if templates_result:
                templates_result['accuracy_score'] = max(templates_result.get('accuracy_score', 0), avg_ai_score)

        emit_progress(args.job_id, 'verifying', 90, 'Verifying conversion with AI')
        should_verify_with_ai = use_ai and bool(args.gemini_api_key)
        gemini_verifier = GeminiVerifier(args.gemini_api_key) if should_verify_with_ai else None
        verification_result = {
            'enabled': bool(gemini_verifier and gemini_verifier.enabled),
            'models_verification': {'enabled': False},
            'views_verification': {'enabled': False},
            'ai_summary': {}
        }

        if gemini_verifier and gemini_verifier.enabled:
            ai_summary = gemini_verifier.generate_summary({
                'models': models_result,
                'views': views_result,
                'urls': urls_result,
                'templates': templates_result
            })
            verification_result['ai_summary'] = ai_summary

        # Final accuracy report after all enhancements
        if 'accuracy_orchestrator' in locals():
            emit_progress(args.job_id, 'generating_accuracy_report', 98, 'Generating final accuracy report')
            
            # Recalculate based on updated scores
            overall_accuracy = accuracy_orchestrator.calculate_overall_accuracy()
            accuracy_report = accuracy_orchestrator.generate_accuracy_report()
            ProgressEmitter.emit_custom(args.job_id, 'accuracy_report', accuracy_report)

        emit_progress(args.job_id, 'generating_report', 99, 'Preparing final summary')
        reporter = SummaryReporter()
        report = reporter.generate({
            'analysis': analysis_result,
            'models': models_result,
            'views': views_result,
            'urls': urls_result,
            'templates': templates_result,
            'verification': verification_result,
            'ai_enhancements': ai_enhancements
        })

        emit_progress(args.job_id, 'completed', 100, 'Conversion completed successfully')
        ProgressEmitter.emit_result({
            'success': True,
            'report': report,
            'output_path': args.output_path
        })

        logger.info(f"Conversion completed successfully for job {args.job_id}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        ProgressEmitter.emit_error(args.job_id, str(e))
        sys.exit(1)


def _write_improved_content_to_disk(
    flask_project_path, models_result, views_result,
    urls_result, templates_result, log
):
    """Write accuracy-improved content back to the on-disk project files."""
    import glob

    def _write(pattern, content, label):
        if not content:
            return
        matches = glob.glob(str(flask_project_path / '**' / pattern), recursive=True)
        for match_path in matches:
            try:
                with open(match_path, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                log.info(f"Wrote improved {label} to {match_path}")
            except Exception as exc:
                log.warning(f"Failed to write improved {label} to {match_path}: {exc}")

    _write('models.py', models_result.get('converted_content'), 'models')
    _write('routes.py', views_result.get('converted_content'), 'routes')
    _write('urls.py', urls_result.get('converted_content'), 'urls')
    # Templates are HTML; skip automatic overwrite since they span many files.


if __name__ == '__main__':
    main()
