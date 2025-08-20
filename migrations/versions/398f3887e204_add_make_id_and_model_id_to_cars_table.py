"""Create initial car tables with make_id and model_id"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '398f3887e204'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'makes',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', mysql.VARCHAR(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index('uq_makes_name', 'makes', ['name'], unique=True)

    op.create_table(
        'models',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', mysql.VARCHAR(length=64), nullable=False),
        sa.Column('make_id', mysql.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['make_id'], ['makes.id'], name='fk_models_make'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    op.create_table(
        'cars',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('make_id', mysql.INTEGER(), nullable=False),
        sa.Column('model_id', mysql.INTEGER(), nullable=False),
        sa.Column('year', mysql.INTEGER(), nullable=False),
        sa.Column('category', mysql.VARCHAR(length=64), nullable=False),
        sa.ForeignKeyConstraint(['make_id'], ['makes.id'], name='fk_cars_make'),
        sa.ForeignKeyConstraint(['model_id'], ['models.id'], name='fk_cars_model'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

def downgrade():
    op.drop_table('cars')
    op.drop_table('models')
    op.drop_table('makes')

