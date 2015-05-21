"""empty message

Revision ID: 96ad9704add
Revises: 33578d0361f7
Create Date: 2015-05-17 23:09:02.011639

"""

# revision identifiers, used by Alembic.
revision = '96ad9704add'
down_revision = '33578d0361f7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('study_users',
    sa.Column('study_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['study_id'], ['studies.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('study_users')
    ### end Alembic commands ###
