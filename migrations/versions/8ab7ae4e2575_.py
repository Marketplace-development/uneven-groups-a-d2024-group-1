"""empty message

Revision ID: 8ab7ae4e2575
Revises: 
Create Date: 2024-11-20 16:37:27.013105

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8ab7ae4e2575'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('phonenumber', sa.String(length=15), nullable=False),
    sa.Column('location_name', sa.String(length=100), nullable=False),
    sa.Column('location_type', sa.String(length=50), nullable=False),
    sa.Column('country', sa.String(length=50), nullable=False),
    sa.Column('postal_code', sa.String(length=10), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=False),
    sa.Column('street_number', sa.String(length=10), nullable=False),
    sa.Column('bus', sa.String(length=10), nullable=True),
    sa.Column('chairs', sa.Integer(), nullable=False),
    sa.Column('monday_open', sa.String(length=5), nullable=True),
    sa.Column('monday_close', sa.String(length=5), nullable=True),
    sa.Column('tuesday_open', sa.String(length=5), nullable=True),
    sa.Column('tuesday_close', sa.String(length=5), nullable=True),
    sa.Column('wednesday_open', sa.String(length=5), nullable=True),
    sa.Column('wednesday_close', sa.String(length=5), nullable=True),
    sa.Column('thursday_open', sa.String(length=5), nullable=True),
    sa.Column('thursday_close', sa.String(length=5), nullable=True),
    sa.Column('friday_open', sa.String(length=5), nullable=True),
    sa.Column('friday_close', sa.String(length=5), nullable=True),
    sa.Column('saturday_open', sa.String(length=5), nullable=True),
    sa.Column('saturday_close', sa.String(length=5), nullable=True),
    sa.Column('sunday_open', sa.String(length=5), nullable=True),
    sa.Column('sunday_close', sa.String(length=5), nullable=True),
    sa.Column('location_picture', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('student')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))

    op.create_table('student',
    sa.Column('studentid', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('studentid', name='student_pkey')
    )
    op.drop_table('reservation')
    op.drop_table('locations')
    # ### end Alembic commands ###
