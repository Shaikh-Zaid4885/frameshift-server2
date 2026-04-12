"""
Advanced Forms & Database Queries Conversion Accuracy Improver
Handles complex Django forms → Flask-WTF and QuerySet → SQLAlchemy conversion
"""

import re
from typing import Dict, List, Optional, Tuple


class FormsQueriesAccuracyImprover:
    """
    Improves accuracy of Django Forms and Database Queries conversion
    Handles: form fields, validation, queries, filters, relationships, aggregations
    """

    def __init__(self):
        self.field_mappings = self._build_field_mappings()
        self.widget_mappings = self._build_widget_mappings()
        self.query_mappings = self._build_query_mappings()

    def _build_field_mappings(self) -> Dict[str, str]:
        """Map Django form fields to Flask-WTF"""
        return {
            'CharField': 'StringField',
            'IntegerField': 'IntegerField',
            'BooleanField': 'BooleanField',
            'DateField': 'DateField',
            'DateTimeField': 'DateTimeField',
            'EmailField': 'EmailField',
            'URLField': 'URLField',
            'FileField': 'FileField',
            'ImageField': 'FileField',
            'ChoiceField': 'SelectField',
            'MultipleChoiceField': 'SelectMultipleField',
            'FloatField': 'FloatField',
            'DecimalField': 'DecimalField',
            'TimeField': 'TimeField',
            'SlugField': 'StringField',
            'TextChoiceField': 'SelectField',
        }

    def _build_widget_mappings(self) -> Dict[str, str]:
        """Map Django widgets to Flask-WTF"""
        return {
            'TextInput': 'StringField',
            'Textarea': 'TextAreaField',
            'EmailInput': 'EmailField',
            'URLInput': 'URLField',
            'NumberInput': 'IntegerField',
            'Select': 'SelectField',
            'CheckboxInput': 'BooleanField',
            'RadioSelect': 'RadioField',
            'CheckboxSelectMultiple': 'SelectMultipleField',
            'DateInput': 'DateField',
            'DateTimeInput': 'DateTimeField',
            'TimeInput': 'TimeField',
            'FileInput': 'FileField',
            'PasswordInput': 'PasswordField',
            'HiddenInput': 'HiddenField',
        }

    def _build_query_mappings(self) -> Dict[str, str]:
        """Map Django QuerySet methods to SQLAlchemy"""
        return {
            'filter': 'filter',
            'exclude': 'filter(~)',
            'all': 'all',
            'get': 'first',
            'create': 'add',
            'update': 'update',
            'delete': 'delete',
            'exists': 'count() > 0',
            'count': 'count',
            'first': 'first',
            'last': 'all()[-1]',
            'values': 'with_entities',
            'values_list': 'with_entities',
            'order_by': 'order_by',
            'distinct': 'distinct',
            'select_related': 'joinedload',
            'prefetch_related': 'with_polymorphic',
        }

    def improve_form_fields(self, django_form: str) -> str:
        """
        Convert Django form fields to Flask-WTF
        """
        improved = django_form
        
        # Convert field definitions
        for django_field, flask_field in self._build_field_mappings().items():
            improved = re.sub(
                rf"{django_field}\(",
                f"{flask_field}(",
                improved
            )
        
        # Convert validators
        improved = self._convert_validators(improved)
        
        # Convert field options
        improved = self._convert_field_options(improved)
        
        # Convert widgets
        improved = self._convert_widgets(improved)
        
        return improved

    def _convert_validators(self, code: str) -> str:
        """
        Convert Django validators to Flask-WTF validators
        """
        validators_map = {
            'validators.EmailValidator': 'Email()',
            'validators.URLValidator': 'URL()',
            'validators.MinValueValidator': 'NumberRange(min=...)',
            'validators.MaxValueValidator': 'NumberRange(max=...)',
            'validators.MinLengthValidator': 'Length(min=...)',
            'validators.MaxLengthValidator': 'Length(max=...)',
            'validators.RegexValidator': 'Regexp(...)',
            'validators.DecimalValidator': 'NumberRange()',
            'validators.FileExtensionValidator': 'FileAllowed(...)',
        }
        
        for django_validator, flask_validator in validators_map.items():
            code = code.replace(django_validator, flask_validator)
        
        # Convert validators list
        code = re.sub(
            r"validators=\[\s*([^\]]+)\s*\]",
            lambda m: f"validators=[{self._extract_validators(m.group(1))}]",
            code
        )
        
        return code

    def _extract_validators(self, validators_str: str) -> str:
        """Extract and convert individual validators"""
        validators = re.findall(r'(\w+)\([^)]*\)', validators_str)
        return ", ".join(validators)

    def _convert_field_options(self, code: str) -> str:
        """
        Convert Django field options to Flask-WTF equivalents
        """
        options_map = {
            'max_length': 'maxLength',  # HTML attribute
            'min_length': 'minLength',
            'required': 'validators=[DataRequired()]',
            'label': 'label',
            'help_text': 'description',
            'error_messages': 'error_messages',
            'initial': 'default',
            'disabled': 'render_kw={"disabled": True}',
            'choices': 'choices',
        }
        
        for django_option, flask_option in options_map.items():
            code = code.replace(django_option, flask_option)
        
        # Convert required=True
        code = code.replace(
            "required=True",
            "validators=[DataRequired()]"
        )
        
        code = code.replace(
            "required=False",
            "validators=[]"
        )
        
        return code

    def _convert_widgets(self, code: str) -> str:
        """
        Convert Django widgets to Flask-WTF
        """
        # Remove widget specifications (Flask-WTF infers from field type)
        code = re.sub(
            r",\s*widget=\w+\(\)",
            "",
            code
        )
        
        # Convert specific widget configurations
        for django_widget, flask_field in self._build_widget_mappings().items():
            code = code.replace(f"widget={django_widget}()", f"# {flask_field}")
        
        return code

    def improve_form_validation(self, django_form: str) -> str:
        """
        Improve form validation method conversion
        """
        improved = django_form
        
        # Convert clean() method
        improved = improved.replace(
            "def clean(self):",
            "def validate(self):"
        )
        
        # Convert field-specific clean methods
        improved = re.sub(
            r"def clean_(\w+)\(self\):",
            r"def validate_\1(self, field):",
            improved
        )
        
        # Convert ValidationError
        improved = re.sub(
            r"raise ValidationError\((.*?)\)",
            r"raise ValidationError(\1)",
            improved
        )
        
        # Convert error messages
        improved = re.sub(
            r"self\.add_error\((['\"][^'\"]+['\"]|\w+),\s*([^)]+)\)",
            r"self.\1.errors.append(\2)",
            improved
        )
        
        return improved

    def improve_model_choices(self, django_form: str) -> str:
        """
        Convert Django choices to Flask-WTF SelectField choices
        """
        improved = django_form
        
        # Convert choices=CHOICES_LIST pattern
        improved = re.sub(
            r"choices=(\w+)",
            r"choices=\1",
            improved
        )
        
        # Convert inline choices: choices=[(1, 'One'), (2, 'Two')]
        improved = re.sub(
            r"choices=\[\s*\(([^\]]+)\)\s*\]",
            lambda m: f"choices=[{m.group(1)}]",
            improved
        )
        
        return improved

    def improve_database_queries(self, django_code: str) -> str:
        """
        Convert Django QuerySet operations to SQLAlchemy
        """
        improved = django_code
        
        # Convert Model.objects.all() → db.session.query(Model).all()
        improved = re.sub(
            r"(\w+)\.objects\.all\(\)",
            r"db.session.query(\1).all()",
            improved
        )
        
        # Convert Model.objects.filter() → db.session.query(Model).filter()
        improved = re.sub(
            r"(\w+)\.objects\.filter\(([^)]+)\)",
            r"db.session.query(\1).filter(\2)",
            improved
        )
        
        # Convert Model.objects.exclude() → db.session.query(Model).filter(~condition)
        improved = re.sub(
            r"(\w+)\.objects\.exclude\(([^)]+)\)",
            r"db.session.query(\1).filter(~(\2))",
            improved
        )
        
        # Convert Model.objects.get() → db.session.query(Model).filter(...).first()
        improved = re.sub(
            r"(\w+)\.objects\.get\(([^)]+)\)",
            r"db.session.query(\1).filter(\2).first()",
            improved
        )
        
        # Convert Model.objects.create() → db.session.add()
        improved = re.sub(
            r"(\w+)\.objects\.create\(([^)]+)\)",
            lambda m: f"obj = {m.group(1)}({m.group(2)}); db.session.add(obj); db.session.commit()",
            improved
        )
        
        # Convert QuerySet methods
        improved = self._convert_queryset_methods(improved)
        
        return improved

    def _convert_queryset_methods(self, code: str) -> str:
        """Convert specific QuerySet methods"""
        # Convert exists()
        code = re.sub(
            r"(\w+)\.exists\(\)",
            r"db.session.query(\1).count() > 0",
            code
        )
        
        # Convert count()
        code = re.sub(
            r"(\w+)\.count\(\)",
            r"db.session.query(\1).count()",
            code
        )
        
        # Convert first()
        code = re.sub(
            r"(\w+)\.first\(\)",
            r"db.session.query(\1).first()",
            code
        )
        
        # Convert last()
        code = re.sub(
            r"(\w+)\.last\(\)",
            r"db.session.query(\1).order_by(\1.id.desc()).first()",
            code
        )
        
        # Convert distinct()
        code = re.sub(
            r"\.distinct\(\)",
            ".distinct()",
            code
        )
        
        # Convert values()
        code = re.sub(
            r"\.values\(([^)]+)\)",
            r".with_entities(\1)",
            code
        )
        
        # Convert order_by()
        code = re.sub(
            r"\.order_by\(([^)]+)\)",
            r".order_by(\1)",
            code
        )
        
        # Convert select_related()
        code = re.sub(
            r"\.select_related\(([^)]+)\)",
            r".joinedload(\1)",
            code
        )
        
        return code

    def improve_query_filters(self, code: str) -> str:
        """
        Improve query filter conversion
        Django: Model.objects.filter(field__lookup=value)
        SQLAlchemy: db.session.query(Model).filter(Model.field.lookup(value))
        """
        improved = code
        
        # Convert __exact (default)
        improved = re.sub(
            r"(\w+)__exact",
            r"\1",
            improved
        )
        
        # Convert __iexact
        improved = re.sub(
            r"(\w+)__iexact",
            r"\1.ilike",
            improved
        )
        
        # Convert __contains
        improved = re.sub(
            r"(\w+)__contains",
            r"\1.contains",
            improved
        )
        
        # Convert __icontains
        improved = re.sub(
            r"(\w+)__icontains",
            r"\1.ilike('%' + value + '%')",
            improved
        )
        
        # Convert __startswith
        improved = re.sub(
            r"(\w+)__startswith",
            r"\1.like(value + '%')",
            improved
        )
        
        # Convert __istartswith
        improved = re.sub(
            r"(\w+)__istartswith",
            r"\1.ilike(value + '%')",
            improved
        )
        
        # Convert __endswith
        improved = re.sub(
            r"(\w+)__endswith",
            r"\1.like('%' + value)",
            improved
        )
        
        # Convert __iendswith
        improved = re.sub(
            r"(\w+)__iendswith",
            r"\1.ilike('%' + value)",
            improved
        )
        
        # Convert __gt, __gte, __lt, __lte
        improved = re.sub(r"(\w+)__gt", r"\1 >", improved)
        improved = re.sub(r"(\w+)__gte", r"\1 >=", improved)
        improved = re.sub(r"(\w+)__lt", r"\1 <", improved)
        improved = re.sub(r"(\w+)__lte", r"\1 <=", improved)
        
        # Convert __in
        improved = re.sub(
            r"(\w+)__in",
            r"\1.in_()",
            improved
        )
        
        # Convert __isnull
        improved = re.sub(
            r"(\w+)__isnull",
            r"\1.is_(None)",
            improved
        )
        
        # Convert __range
        improved = re.sub(
            r"(\w+)__range",
            r"\1.between",
            improved
        )
        
        # Convert __year, __month, __day
        improved = re.sub(
            r"(\w+)__year",
            r"extract('year', \1)",
            improved
        )
        
        improved = re.sub(
            r"(\w+)__month",
            r"extract('month', \1)",
            improved
        )
        
        improved = re.sub(
            r"(\w+)__day",
            r"extract('day', \1)",
            improved
        )
        
        return improved

    def improve_query_aggregation(self, code: str) -> str:
        """
        Convert Django aggregation to SQLAlchemy
        """
        improved = code
        
        # Convert Count
        improved = improved.replace(
            "Count('",
            "func.count("
        )
        
        # Convert Sum
        improved = improved.replace(
            "Sum('",
            "func.sum("
        )
        
        # Convert Avg
        improved = improved.replace(
            "Avg('",
            "func.avg("
        )
        
        # Convert Min
        improved = improved.replace(
            "Min('",
            "func.min("
        )
        
        # Convert Max
        improved = improved.replace(
            "Max('",
            "func.max("
        )
        
        # Convert annotate
        improved = re.sub(
            r"\.annotate\((\w+)=([^)]+)\)",
            r".add_columns(\2.label('\1'))",
            improved
        )
        
        # Convert values and annotate to group by
        improved = re.sub(
            r"\.values\(([^)]+)\)\.annotate\(([^)]+)\)",
            r".group_by(\1).add_columns(\2)",
            improved
        )
        
        return improved

    def improve_query_joins(self, code: str) -> str:
        """
        Convert Django joins to SQLAlchemy
        """
        improved = code
        
        # select_related is implicit in SQLAlchemy with joinedload
        improved = improved.replace(
            ".select_related(",
            ".joinedload("
        )
        
        # prefetch_related for many-to-many
        improved = improved.replace(
            ".prefetch_related(",
            ".with_polymorphic("
        )
        
        # Add join() for explicit joins
        improved = re.sub(
            r"\.join\(([^)]+)\)",
            r".join(\1)",
            improved
        )
        
        return improved

    def add_session_management(self, code: str) -> str:
        """
        Add proper session management to queries
        """
        if "db.session.query" in code and "db.session.commit()" not in code:
            # Add session management pattern
            session_pattern = '''
try:
    # Query
    result = db.session.query(Model).filter(...).all()
    return result
except Exception as e:
    db.session.rollback()
    raise
finally:
    pass  # Session automatically cleaned up
'''
            if "except" not in code:
                code = code + "\n" + session_pattern
        
        return code

    def add_imports(self, code: str) -> str:
        """Add necessary imports for queries and forms"""
        needed_imports = []
        
        if "db.session.query" in code:
            needed_imports.append("from sqlalchemy import func, extract")
            needed_imports.append("from flask_sqlalchemy import SQLAlchemy")
        
        if "StringField" in code or "EmailField" in code:
            needed_imports.append("from wtforms import StringField, IntegerField, BooleanField, SelectField")
            needed_imports.append("from wtforms.validators import DataRequired, Email, Length, Regexp")
        
        if needed_imports:
            import_section = "\n".join(set(needed_imports))
            if not any(imp in code for imp in needed_imports):
                code = import_section + "\n\n" + code
        
        return code

    def validate_conversion(self, original: str, converted: str) -> Dict:
        """
        Validate forms and queries conversion accuracy
        Returns: accuracy score and issues found
        """
        issues = []
        score = 100
        
        # Count form fields
        original_fields = len(re.findall(r"\w+Field\(", original))
        converted_fields = len(re.findall(r"\w+Field\(", converted))
        
        if original_fields > converted_fields:
            issues.append(f"Form field count mismatch: {original_fields} → {converted_fields}")
            score -= 15
        
        # Count queries
        original_queries = len(re.findall(r"\.objects\.", original))
        converted_queries = len(re.findall(r"db\.session", converted))
        
        if original_queries > converted_queries * 0.8:
            issues.append(f"Query conversion incomplete: {original_queries} → {converted_queries}")
            score -= 15
        
        # Check for unconverted patterns
        if ".objects." in converted:
            issues.append("Found unconverted Django ORM patterns")
            score -= 20
        
        if "ValidationError" in original and "ValidationError" not in converted:
            issues.append("Missing ValidationError handling")
            score -= 10
        
        # Check for validators
        if "validators=" in original and "validators=" not in converted:
            issues.append("Missing field validators conversion")
            score -= 10
        
        # Check for query filters
        if "__" in original and "__" in converted:
            issues.append("Found unconverted Django filter lookups")
            score -= 15
        
        return {
            'accuracy_score': max(0, score),
            'issues': issues,
            'field_count': converted_fields,
            'query_count': converted_queries,
            'is_valid': len(issues) == 0 and score >= 80
        }
