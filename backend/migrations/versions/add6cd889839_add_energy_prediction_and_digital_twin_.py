"""Add energy prediction and digital twin tables

Revision ID: add6cd889839
Revises: f3942ccb8721
Create Date: 2025-10-08 07:42:55.657886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add6cd889839'
down_revision: Union[str, None] = 'f3942ccb8721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建energy_predictions表
    op.create_table('energy_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('predicted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('target_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('energy_level', sa.String(length=20), nullable=False, comment='精力等级: high/medium/low'),
        sa.Column('energy_score', sa.Float(), nullable=False, comment='精力分数(1-10)'),
        sa.Column('confidence', sa.Float(), nullable=False, comment='预测置信度(0-1)'),
        sa.Column('factors', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='影响因素权重(JSON)'),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='建议列表(JSON)'),
        sa.Column('actual_energy', sa.Float(), nullable=True, comment='实际精力(用于验证预测准确性)'),
        sa.Column('prediction_error', sa.Float(), nullable=True, comment='预测误差(abs(actual - predicted))'),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_energy_predictions_id', 'energy_predictions', ['id'])
    op.create_index('ix_energy_predictions_predicted_at', 'energy_predictions', ['predicted_at'])
    op.create_index('ix_energy_predictions_target_time', 'energy_predictions', ['target_time'])
    op.create_index('ix_energy_predictions_user_id', 'energy_predictions', ['user_id'])
    op.create_index('ix_energy_predictions_user_target', 'energy_predictions', ['user_id', 'target_time'])

    # 创建energy_baselines表
    op.create_table('energy_baselines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avg_energy', sa.Float(), nullable=False, comment='平均精力(1-10)'),
        sa.Column('high_threshold', sa.Float(), nullable=False, comment='高精力阈值'),
        sa.Column('low_threshold', sa.Float(), nullable=False, comment='低精力阈值'),
        sa.Column('optimal_sleep', sa.Float(), nullable=False, server_default='8.0', comment='最佳睡眠时长(小时)'),
        sa.Column('data_points', sa.Integer(), nullable=False, server_default='0', comment='用于计算基线的数据点数'),
        sa.Column('calculation_period_days', sa.Integer(), nullable=False, server_default='30', comment='计算周期(天)'),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_energy_baselines_id', 'energy_baselines', ['id'])
    op.create_index('ix_energy_baselines_user_id', 'energy_baselines', ['user_id'])

    # 创建energy_patterns表
    op.create_table('energy_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pattern_type', sa.String(length=50), nullable=False, comment='模式类型'),
        sa.Column('description', sa.Text(), nullable=False, comment='模式描述'),
        sa.Column('confidence', sa.Float(), nullable=False, comment='模式置信度(0-1)'),
        sa.Column('frequency', sa.String(length=50), nullable=True, comment='发生频率'),
        sa.Column('triggers', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='触发因素'),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='针对性建议'),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_occurrence', sa.DateTime(timezone=True), nullable=True),
        sa.Column('occurrence_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_energy_patterns_id', 'energy_patterns', ['id'])
    op.create_index('ix_energy_patterns_user_id', 'energy_patterns', ['user_id'])
    op.create_index('ix_energy_patterns_user_type', 'energy_patterns', ['user_id', 'pattern_type'])

    # 创建environment_data表
    op.create_table('environment_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False, comment='位置(城市名或经纬度)'),
        sa.Column('temperature', sa.Float(), nullable=True, comment='温度(℃)'),
        sa.Column('weather', sa.String(length=50), nullable=True, comment='天气状况(晴/阴/雨等)'),
        sa.Column('pressure', sa.Float(), nullable=True, comment='气压(hPa)'),
        sa.Column('humidity', sa.Float(), nullable=True, comment='湿度(%)'),
        sa.Column('uv_index', sa.Float(), nullable=True, comment='紫外线指数'),
        sa.Column('air_quality', sa.Integer(), nullable=True, comment='空气质量指数(AQI)'),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='API原始数据(JSON)'),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='openweather', comment='数据来源API'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_environment_data_id', 'environment_data', ['id'])
    op.create_index('ix_environment_data_recorded_at', 'environment_data', ['recorded_at'])
    op.create_index('ix_environment_data_user_id', 'environment_data', ['user_id'])
    op.create_index('ix_environment_data_location_recorded', 'environment_data', ['location', 'recorded_at'])
    op.create_index('ix_environment_data_user_recorded', 'environment_data', ['user_id', 'recorded_at'])


def downgrade() -> None:
    op.drop_index('ix_environment_data_user_recorded', table_name='environment_data')
    op.drop_index('ix_environment_data_location_recorded', table_name='environment_data')
    op.drop_index('ix_environment_data_user_id', table_name='environment_data')
    op.drop_index('ix_environment_data_recorded_at', table_name='environment_data')
    op.drop_index('ix_environment_data_id', table_name='environment_data')
    op.drop_table('environment_data')

    op.drop_index('ix_energy_patterns_user_type', table_name='energy_patterns')
    op.drop_index('ix_energy_patterns_user_id', table_name='energy_patterns')
    op.drop_index('ix_energy_patterns_id', table_name='energy_patterns')
    op.drop_table('energy_patterns')

    op.drop_index('ix_energy_baselines_user_id', table_name='energy_baselines')
    op.drop_index('ix_energy_baselines_id', table_name='energy_baselines')
    op.drop_table('energy_baselines')

    op.drop_index('ix_energy_predictions_user_target', table_name='energy_predictions')
    op.drop_index('ix_energy_predictions_user_id', table_name='energy_predictions')
    op.drop_index('ix_energy_predictions_target_time', table_name='energy_predictions')
    op.drop_index('ix_energy_predictions_predicted_at', table_name='energy_predictions')
    op.drop_index('ix_energy_predictions_id', table_name='energy_predictions')
    op.drop_table('energy_predictions')
