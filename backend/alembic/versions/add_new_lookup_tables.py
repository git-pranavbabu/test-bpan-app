"""Initial tables creation - complete schema

Revision ID: add_new_lookup_tables
Revises: 
Create Date: 2026-05-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'add_new_lookup_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('countries',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('region', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('manufacturers',
    sa.Column('code', sa.String(length=3), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('country_code', sa.String(length=2), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['country_code'], ['countries.code'], ),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('battery_capacities',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('value_kwh', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('battery_chemistries',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('nominal_voltages',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('value_v', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('cell_origins',
    sa.Column('code', sa.String(length=2), nullable=False),
    sa.Column('country_name', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('extinguisher_classes',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('class_code', sa.String(length=10), nullable=True),
    sa.Column('class_name', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('factory_codes',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('factory_name', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('manufacturing_years',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('manufacturing_months',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('month_num', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('manufacturing_dates',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('day_num', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('tac_numbers',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('tac_number', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('cell_types',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('type_name', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('pack_construction_types',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('construction_type', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('module_construction_types',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('construction_type', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('cooling_systems',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('cooling_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('internal_resistances',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('value_mohm', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('battery_weights',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('value_kg', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('battery_warranties',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('years', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('power_80_soc',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('value_kw', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('power_20_soc',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('value_kw', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('code', sa.String(length=10), nullable=True),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('value_kw')
    )
    
    op.create_table('carbon_footprints',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('value_kgco2ekwh', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('number_of_cells',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('dimensions',
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('length_mm', sa.Integer(), nullable=False),
    sa.Column('width_mm', sa.Integer(), nullable=False),
    sa.Column('height_mm', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('code')
    )
    
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('admin', 'production_team', 'quality_team', name='userrole'), nullable=False),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    op.create_table('battery_models',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('manufacturer_code', sa.String(length=3), nullable=False),
    sa.Column('capacity_code', sa.String(length=2), nullable=False),
    sa.Column('chemistry_code', sa.String(length=1), nullable=False),
    sa.Column('voltage_code', sa.String(length=2), nullable=False),
    sa.Column('cell_origin_code', sa.String(length=2), nullable=False),
    sa.Column('extinguisher_code', sa.String(length=1), nullable=False),
    sa.Column('factory_code', sa.String(length=1), nullable=False),
    sa.Column('tac_code', sa.String(length=10), nullable=False),
    sa.Column('internal_resistance_code', sa.String(length=10), nullable=False),
    sa.Column('warranty_code', sa.String(length=10), nullable=False),
    sa.Column('cell_type_code', sa.String(length=1), nullable=False),
    sa.Column('pack_construction_code', sa.String(length=10), nullable=False),
    sa.Column('module_construction_code', sa.String(length=10), nullable=False),
    sa.Column('cooling_code', sa.String(length=1), nullable=False),
    sa.Column('num_cells_code', sa.String(length=10), nullable=False),
    sa.Column('weight_code', sa.String(length=10), nullable=False),
    sa.Column('dimensions_code', sa.String(length=20), nullable=False),
    sa.Column('power_80_soc_code', sa.String(length=10), nullable=False),
    sa.Column('power_20_soc_value', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('carbon_footprint_code', sa.String(length=10), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['country_code'], ['countries.code'], ),
    sa.ForeignKeyConstraint(['manufacturer_code'], ['manufacturers.code'], ),
    sa.ForeignKeyConstraint(['capacity_code'], ['battery_capacities.code'], ),
    sa.ForeignKeyConstraint(['chemistry_code'], ['battery_chemistries.code'], ),
    sa.ForeignKeyConstraint(['voltage_code'], ['nominal_voltages.code'], ),
    sa.ForeignKeyConstraint(['cell_origin_code'], ['cell_origins.code'], ),
    sa.ForeignKeyConstraint(['extinguisher_code'], ['extinguisher_classes.code'], ),
    sa.ForeignKeyConstraint(['factory_code'], ['factory_codes.code'], ),
    sa.ForeignKeyConstraint(['tac_code'], ['tac_numbers.code'], ),
    sa.ForeignKeyConstraint(['cell_type_code'], ['cell_types.code'], ),
    sa.ForeignKeyConstraint(['pack_construction_code'], ['pack_construction_types.code'], ),
    sa.ForeignKeyConstraint(['module_construction_code'], ['module_construction_types.code'], ),
    sa.ForeignKeyConstraint(['cooling_code'], ['cooling_systems.code'], ),
    sa.ForeignKeyConstraint(['internal_resistance_code'], ['internal_resistances.code'], ),
    sa.ForeignKeyConstraint(['warranty_code'], ['battery_warranties.code'], ),
    sa.ForeignKeyConstraint(['num_cells_code'], ['number_of_cells.code'], ),
    sa.ForeignKeyConstraint(['weight_code'], ['battery_weights.code'], ),
    sa.ForeignKeyConstraint(['dimensions_code'], ['dimensions.code'], ),
    sa.ForeignKeyConstraint(['power_80_soc_code'], ['power_80_soc.code'], ),
    sa.ForeignKeyConstraint(['carbon_footprint_code'], ['carbon_footprints.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_battery_models_name'), 'battery_models', ['name'], unique=False)
    
    op.create_table('bpans',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('code_21char', sa.String(length=21), nullable=False),
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('year_code', sa.String(length=1), nullable=False),
    sa.Column('month_code', sa.String(length=1), nullable=False),
    sa.Column('date_code', sa.String(length=1), nullable=False),
    sa.Column('serial_number', sa.Integer(), nullable=False),
    sa.Column('full_data_html', sa.Text(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['date_code'], ['manufacturing_dates.code'], ),
    sa.ForeignKeyConstraint(['model_id'], ['battery_models.id'], ),
    sa.ForeignKeyConstraint(['month_code'], ['manufacturing_months.code'], ),
    sa.ForeignKeyConstraint(['year_code'], ['manufacturing_years.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bpans_code_21char'), 'bpans', ['code_21char'], unique=True)
    
    op.create_table('audit_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('entity_type', sa.String(length=50), nullable=True),
    sa.Column('entity_id', sa.String(length=100), nullable=True),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('system_config',
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('value', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('key')
    )


def downgrade() -> None:
    op.drop_table('system_config')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_bpans_code_21char'), table_name='bpans')
    op.drop_table('bpans')
    op.drop_index(op.f('ix_battery_models_name'), table_name='battery_models')
    op.drop_table('battery_models')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_table('dimensions')
    op.drop_table('number_of_cells')
    op.drop_table('carbon_footprints')
    op.drop_table('power_20_soc')
    op.drop_table('power_80_soc')
    op.drop_table('battery_warranties')
    op.drop_table('battery_weights')
    op.drop_table('internal_resistances')
    op.drop_table('cooling_systems')
    op.drop_table('module_construction_types')
    op.drop_table('pack_construction_types')
    op.drop_table('cell_types')
    op.drop_table('tac_numbers')
    op.drop_table('manufacturing_dates')
    op.drop_table('manufacturing_months')
    op.drop_table('manufacturing_years')
    op.drop_table('factory_codes')
    op.drop_table('extinguisher_classes')
    op.drop_table('cell_origins')
    op.drop_table('nominal_voltages')
    op.drop_table('battery_chemistries')
    op.drop_table('battery_capacities')
    op.drop_table('manufacturers')
    op.drop_table('countries')