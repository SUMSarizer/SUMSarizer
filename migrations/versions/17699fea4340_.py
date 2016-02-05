"""empty message

Revision ID: 17699fea4340
Revises: 371b8b747fb9
Create Date: 2015-05-27 13:50:45.133915

"""

# revision identifiers, used by Alembic.
revision = '17699fea4340'
down_revision = '371b8b747fb9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'labelled_datasets_dataset_id_fkey', 'labelled_datasets', type_='foreignkey')
    op.create_foreign_key(None, 'labelled_datasets', 'datasets', ['dataset_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'labelled_datasets', type_='foreignkey')
    op.create_foreign_key(u'labelled_datasets_dataset_id_fkey', 'labelled_datasets', 'studies', ['dataset_id'], ['id'])
    ### end Alembic commands ###