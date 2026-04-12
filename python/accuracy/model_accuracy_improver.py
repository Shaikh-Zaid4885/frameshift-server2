"""
Advanced Model Conversion Accuracy Improver
Handles complex Django model patterns with high accuracy
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ModelAccuracyImprover:
    """
    Improves accuracy of Django model → SQLAlchemy conversion
    Handles: fields, relationships, inheritance, meta options, validation
    """

    def __init__(self):
        self.field_mappings = self._build_field_mappings()
        self.relationship_patterns = self._build_relationship_patterns()
        self.meta_mappings = self._build_meta_mappings()

    def _build_field_mappings(self) -> Dict[str, str]:
        """Map Django field types to SQLAlchemy column types"""
        return {
            'CharField': 'db.String(255)',
            'TextField': 'db.Text',
            'IntegerField': 'db.Integer',
            'BigIntegerField': 'db.BigInteger',
            'SmallIntegerField': 'db.SmallInteger',
            'FloatField': 'db.Float',
            'DecimalField': 'db.Numeric(precision=19, scale=2)',
            'BooleanField': 'db.Boolean',
            'DateField': 'db.Date',
            'TimeField': 'db.Time',
            'DateTimeField': 'db.DateTime',
            'DurationField': 'db.Interval',
            'EmailField': 'db.String(254)',
            'URLField': 'db.String(200)',
            'FileField': 'db.String(100)',
            'ImageField': 'db.String(100)',
            'SlugField': 'db.String(50)',
            'JSONField': 'db.JSON',
            'UUIDField': 'db.String(36)',
            'BinaryField': 'db.LargeBinary',
        }

    def _build_relationship_patterns(self) -> Dict[str, str]:
        """Map Django relationship patterns to SQLAlchemy"""
        return {
            'ForeignKey': 'db.ForeignKey',
            'OneToOneField': 'db.ForeignKey',
            'ManyToManyField': 'db.Table',
        }

    def _build_meta_mappings(self) -> Dict[str, str]:
        """Map Django Meta options to SQLAlchemy"""
        return {
            'ordering': '__order_by__',
            'verbose_name': '__verbose_name__',
            'verbose_name_plural': '__verbose_name_plural__',
            'unique_together': '__unique_together__',
            'indexes': '__table_args__',
            'db_table': '__tablename__',
            'abstract': '__abstract__',
        }

    def improve_field_conversion(self, django_code: str) -> str:
        """
        Improve field type conversion accuracy
        Handles: max_length, default values, null/blank, validators
        """
        improved = django_code
        
        # Fix CharField with max_length
        improved = re.sub(
            r"models\.CharField\(\s*max_length\s*=\s*(\d+)",
            lambda m: f"db.String({m.group(1)})",
            improved
        )
        
        # Fix DecimalField with precision/scale
        improved = re.sub(
            r"models\.DecimalField\(\s*max_digits\s*=\s*(\d+),\s*decimal_places\s*=\s*(\d+)",
            lambda m: f"db.Numeric(precision={m.group(1)}, scale={m.group(2)})",
            improved
        )
        
        # Fix IntegerField with choices
        improved = self._convert_field_choices(improved)
        
        # Fix default values
        improved = self._convert_field_defaults(improved)
        
        # Fix null/blank to nullable/default
        improved = self._convert_null_blank(improved)
        
        # Fix validators
        improved = self._convert_validators(improved)
        
        return improved

    def _convert_field_choices(self, code: str) -> str:
        """Convert Django choices to SQLAlchemy enums"""
        # Find choice definitions
        choice_pattern = r"(\w+)_CHOICES\s*=\s*\(\s*\((.*?)\)\s*\)"
        
        def replace_choices(match):
            var_name = match.group(1)
            choices_content = match.group(2)
            
            # Extract choice values
            choice_values = re.findall(r"'([^']+)'", choices_content)
            
            # Create enum
            enum_name = f"{var_name.title()}Enum"
            enum_def = f"class {enum_name}(str, enum.Enum):\n"
            
            for choice in choice_values:
                enum_def += f"    {choice.upper()} = '{choice}'\n"
            
            return enum_def
        
        return re.sub(choice_pattern, replace_choices, code, flags=re.DOTALL)

    def _convert_field_defaults(self, code: str) -> str:
        """Convert Django default values to SQLAlchemy"""
        # Handle default=timezone.now()
        code = code.replace(
            "default=timezone.now",
            "default=datetime.datetime.utcnow"
        )
        
        # Handle default=uuid.uuid4
        code = code.replace(
            "default=uuid.uuid4",
            "default=uuid.uuid4"
        )
        
        # Handle callable defaults
        code = re.sub(
            r"default\s*=\s*lambda\s*:\s*([^\)]+)",
            lambda m: f"default=lambda: {m.group(1)}",
            code
        )
        
        return code

    def _convert_null_blank(self, code: str) -> str:
        """Convert Django null/blank to SQLAlchemy nullable"""
        # Convert null=True to nullable=True
        code = code.replace("null=True", "nullable=True")
        code = code.replace("null=False", "nullable=False")
        
        # blank doesn't exist in SQLAlchemy, handle it
        code = re.sub(r",\s*blank=True", "", code)
        code = re.sub(r",\s*blank=False", "", code)
        
        return code

    def _convert_validators(self, code: str) -> str:
        """Convert Django validators to SQLAlchemy checks"""
        # Convert validators to SQLAlchemy Check constraints
        validator_pattern = r"validators\s*=\s*\[(.*?)\]"
        
        def replace_validators(match):
            validators = match.group(1)
            checks = []
            
            if "MinLengthValidator" in validators:
                checks.append("db.CheckConstraint(db.func.length(column) >= min_length, name='check_min_length')")
            
            if "MaxLengthValidator" in validators:
                checks.append("db.CheckConstraint(db.func.length(column) <= max_length, name='check_max_length')")
            
            if "MinValueValidator" in validators:
                checks.append("db.CheckConstraint(column >= min_value, name='check_min_value')")
            
            if "MaxValueValidator" in validators:
                checks.append("db.CheckConstraint(column <= max_value, name='check_max_value')")
            
            if checks:
                return ", ".join(checks)
            return ""
        
        return re.sub(validator_pattern, replace_validators, code)

    def improve_relationship_conversion(self, django_code: str) -> str:
        """
        Improve ForeignKey and relationship conversion
        Handles: cascade options, related_name, through models
        """
        improved = django_code
        
        # Improve ForeignKey conversion
        improved = self._convert_foreign_keys(improved)
        
        # Improve ManyToMany conversion
        improved = self._convert_many_to_many(improved)
        
        # Improve OneToOne conversion
        improved = self._convert_one_to_one(improved)
        
        return improved

    def _convert_foreign_keys(self, code: str) -> str:
        """Convert Django ForeignKey to SQLAlchemy relationships"""
        # Pattern: ForeignKey('AppName.ModelName', on_delete=..., related_name=...)
        
        # Extract cascade options
        code = code.replace(
            "on_delete=models.CASCADE",
            "foreign_keys=[...], cascade='all,delete'"
        )
        code = code.replace(
            "on_delete=models.SET_NULL",
            "foreign_keys=[...], nullable=True"
        )
        code = code.replace(
            "on_delete=models.PROTECT",
            "foreign_keys=[...]"
        )
        
        return code

    def _convert_many_to_many(self, code: str) -> str:
        """Convert Django ManyToManyField to SQLAlchemy relationship"""
        # ManyToMany requires an association table
        m2m_pattern = r"(\w+)\s*=\s*models\.ManyToManyField\('([^']+)'(?:,\s*through='([^']+)')?\)"
        
        def replace_m2m(match):
            field_name = match.group(1)
            related_model = match.group(2)
            through_model = match.group(3)
            
            # Create association table
            assoc_table_name = f"{field_name}_association"
            
            return (
                f"# ManyToMany: {field_name} → {related_model}\n"
                f"{field_name} = db.relationship('{related_model}', "
                f"secondary='{assoc_table_name}')"
            )
        
        return re.sub(m2m_pattern, replace_m2m, code)

    def _convert_one_to_one(self, code: str) -> str:
        """Convert Django OneToOneField to SQLAlchemy relationship"""
        code = code.replace(
            "models.OneToOneField",
            "db.ForeignKey"
        )
        
        # Add unique constraint
        code = re.sub(
            r"(db\.ForeignKey\([^)]+\))",
            lambda m: f"{m.group(1)}, unique=True",
            code
        )
        
        return code

    def improve_model_inheritance(self, django_code: str) -> str:
        """
        Handle Django model inheritance
        Types: Abstract, Multi-table, Proxy
        """
        improved = django_code
        
        # Detect abstract models
        if "class Meta:" in django_code and "abstract = True" in django_code:
            improved = self._convert_abstract_model(improved)
        
        # Detect multi-table inheritance
        elif re.search(r"class \w+\(models\.Model.*,\s*\w+\)", django_code):
            improved = self._convert_multi_table_inheritance(improved)
        
        # Detect proxy models
        elif "proxy = True" in django_code:
            improved = self._convert_proxy_model(improved)
        
        return improved

    def _convert_abstract_model(self, code: str) -> str:
        """Convert Django abstract model to SQLAlchemy"""
        # Add SQLAlchemy abstract base
        code = re.sub(
            r"(class \w+\(models\.Model\):)",
            r"class \1(db.Model):\n    __abstract__ = True",
            code
        )
        
        return code

    def _convert_multi_table_inheritance(self, code: str) -> str:
        """Convert Django multi-table inheritance to SQLAlchemy"""
        # Use joined table inheritance
        code = code.replace(
            "class Meta:",
            "class Meta:\n    __mapper_args__ = {'polymorphic_identity': 'derived'}"
        )
        
        return code

    def _convert_proxy_model(self, code: str) -> str:
        """Convert Django proxy model to SQLAlchemy"""
        # Remove proxy model concept (SQLAlchemy uses different patterns)
        code = code.replace("proxy = True", "# Proxy model converted to standard model")
        
        return code

    def improve_meta_options(self, django_code: str) -> str:
        """
        Convert Django Meta options to SQLAlchemy
        Handles: ordering, verbose_name, indexes, unique_together
        """
        improved = django_code
        
        # Convert db_table
        improved = re.sub(
            r"db_table\s*=\s*['\"]([^'\"]+)['\"]",
            r"__tablename__ = '\1'",
            improved
        )
        
        # Convert verbose_name (add to class docstring)
        improved = re.sub(
            r"verbose_name\s*=\s*['\"]([^'\"]+)['\"]",
            lambda m: f"# Verbose Name: {m.group(1)}",
            improved
        )
        
        # Convert unique_together
        improved = re.sub(
            r"unique_together\s*=\s*\(\(([^)]+)\)\)",
            lambda m: f"__table_args__ = (db.UniqueConstraint({m.group(1)}, name='unique_{m.group(1)}'),)",
            improved
        )
        
        # Convert indexes
        improved = re.sub(
            r"indexes\s*=\s*\[\s*models\.Index\(fields=\[([^\]]+)\]\)",
            lambda m: f"__table_args__ = (db.Index('idx_{m.group(1)}', {m.group(1)}),)",
            improved
        )
        
        return improved

    def add_missing_imports(self, code: str) -> str:
        """Add necessary SQLAlchemy imports"""
        imports = [
            "from flask_sqlalchemy import SQLAlchemy",
            "from sqlalchemy.orm import relationship",
            "from sqlalchemy.dialects.postgresql import UUID",
            "import uuid",
            "import datetime",
            "import enum",
        ]
        
        # Check which imports are needed
        needed_imports = []
        
        if "db.String" in code:
            needed_imports.append("from sqlalchemy import String")
        if "db.DateTime" in code:
            needed_imports.append("from sqlalchemy import DateTime")
        if "db.JSON" in code:
            needed_imports.append("from sqlalchemy import JSON")
        if "UUID" in code:
            needed_imports.append("from sqlalchemy.dialects.postgresql import UUID")
        if "relationship" in code:
            needed_imports.append("from sqlalchemy.orm import relationship")
        
        # Add imports at top
        import_section = "\n".join(set(needed_imports))
        
        if import_section and "from sqlalchemy" not in code:
            code = import_section + "\n\n" + code
        
        return code

    def validate_conversion(self, original: str, converted: str) -> Dict:
        """
        Validate conversion accuracy
        Returns: accuracy score and issues found
        """
        issues = []
        score = 100
        
        # Check for common conversion issues
        original_models = len(re.findall(r"class \w+\(models\.Model\)", original))
        converted_models = len(re.findall(r"class \w+\(db\.Model\)", converted))
        
        if original_models != converted_models:
            issues.append(f"Model count mismatch: {original_models} → {converted_models}")
            score -= 10
        
        # Check for unconverted patterns
        if "models." in converted:
            issues.append("Found unconverted Django model patterns")
            score -= 5
        
        if "{{ " in converted:
            issues.append("Found unconverted template tags")
            score -= 5
        
        # Check for missing relationships
        original_fks = len(re.findall(r"ForeignKey", original))
        converted_fks = len(re.findall(r"db.ForeignKey|relationship", converted))
        
        if original_fks > converted_fks:
            issues.append(f"ForeignKey conversion incomplete: {original_fks} → {converted_fks}")
            score -= 15
        
        return {
            'accuracy_score': max(0, score),
            'issues': issues,
            'model_count': converted_models,
            'is_valid': len(issues) == 0
        }
