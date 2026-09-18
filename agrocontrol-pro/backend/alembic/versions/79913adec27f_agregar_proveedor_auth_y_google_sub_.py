"""agregar proveedor_auth y google_sub, quitar usuario maestro

Revision ID: 79913adec27f
Revises: 
Create Date: 2026-09-13 21:05:51.787563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79913adec27f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('proveedor_auth', sa.Enum('LOCAL', 'GOOGLE', name='proveedorautenticacion'), server_default='LOCAL', nullable=True))
        batch_op.add_column(sa.Column('google_sub', sa.String(length=255), nullable=True))
        batch_op.alter_column('password_hash',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=True)
        batch_op.create_index('ix_usuarios_google_sub', ['google_sub'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_index('ix_usuarios_google_sub')
        batch_op.alter_column('password_hash',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=False)
        batch_op.drop_column('google_sub')
        batch_op.drop_column('proveedor_auth')