"""empty message

Revision ID: 27b0c4e13010
Revises: 
Create Date: 2023-08-06 13:41:52.060578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27b0c4e13010'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prts_announce_arkannounce',
    sa.Column('cid', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('category', sa.Integer(), nullable=False),
    sa.Column('displayTime', sa.String(), nullable=False),
    sa.Column('updatedAt', sa.Integer(), nullable=False),
    sa.Column('sticky', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('cid')
    )
    op.create_table('prts_announce_sendmessage',
    sa.Column('msgid', sa.Integer(), nullable=False),
    sa.Column('cid', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('category', sa.Integer(), nullable=False),
    sa.Column('displayTime', sa.Integer(), nullable=False),
    sa.Column('updatedAt', sa.String(), nullable=False),
    sa.Column('sticky', sa.Boolean(), nullable=False),
    sa.Column('header', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('bannerImageUrl', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('msgid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prts_announce_sendmessage')
    op.drop_table('prts_announce_arkannounce')
    # ### end Alembic commands ###
