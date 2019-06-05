"""empty message

Revision ID: 7b63fcb6897d
Revises: 94281f0e0cef
Create Date: 2019-06-03 22:46:23.555512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b63fcb6897d'
down_revision = '94281f0e0cef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('block_submission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('block_num', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('sub_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_block_submission_block_num'), 'block_submission', ['block_num'], unique=False)
    op.create_index(op.f('ix_block_submission_sub_time'), 'block_submission', ['sub_time'], unique=False)
    op.create_index(op.f('ix_block_submission_team_id'), 'block_submission', ['team_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_block_submission_team_id'), table_name='block_submission')
    op.drop_index(op.f('ix_block_submission_sub_time'), table_name='block_submission')
    op.drop_index(op.f('ix_block_submission_block_num'), table_name='block_submission')
    op.drop_table('block_submission')
    # ### end Alembic commands ###