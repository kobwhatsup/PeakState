"""Initial schema with User, Conversation, and HealthData models

Revision ID: 001
Revises:
Create Date: 2025-10-06 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    创建所有初始表
    """
    # 创建coach_type枚举
    op.execute("CREATE TYPE coach_type AS ENUM ('mentor', 'coach', 'doctor', 'zen')")

    # 创建users表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('phone_number', sa.String(20), unique=True, nullable=False, comment='手机号(登录凭证)'),
        sa.Column('hashed_password', sa.String(255), nullable=False, comment='bcrypt加密密码'),
        sa.Column('coach_selection', postgresql.ENUM('mentor', 'coach', 'doctor', 'zen', name='coach_type', create_type=False), nullable=False, server_default='coach', comment='AI教练类型选择'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Asia/Shanghai', comment='用户时区'),

        # 订阅状态
        sa.Column('is_subscribed', sa.Boolean, nullable=False, server_default='false', comment='是否已订阅'),
        sa.Column('subscription_start_date', sa.DateTime(timezone=True), nullable=True, comment='订阅开始时间'),
        sa.Column('subscription_end_date', sa.DateTime(timezone=True), nullable=True, comment='订阅到期时间'),
        sa.Column('subscription_type', sa.String(20), nullable=True, comment='订阅类型(monthly/yearly)'),

        # 试用状态
        sa.Column('is_trial', sa.Boolean, nullable=False, server_default='false', comment='是否试用中'),
        sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True, comment='试用到期时间'),

        # 用户状态
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true', comment='账号是否激活'),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default='false', comment='手机号是否验证'),

        # 用户偏好设置
        sa.Column('morning_briefing_enabled', sa.Boolean, nullable=False, server_default='true', comment='是否启用早报'),
        sa.Column('morning_briefing_time', sa.String(5), nullable=False, server_default='07:00', comment='早报推送时间'),
        sa.Column('evening_review_enabled', sa.Boolean, nullable=False, server_default='true', comment='是否启用晚间复盘'),
        sa.Column('evening_review_time', sa.String(5), nullable=False, server_default='22:00', comment='晚间复盘时间'),

        # 时间戳
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='更新时间'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='最后登录时间'),
    )

    # 创建users表索引
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_phone_number', 'users', ['phone_number'], unique=True)

    # 创建conversations表
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID'),
        sa.Column('title', sa.String(200), nullable=True, comment='对话标题(自动生成或用户设置)'),
        sa.Column('messages', postgresql.JSONB, nullable=False, server_default='[]', comment='对话消息数组'),
        sa.Column('ai_provider_used', sa.String(50), nullable=True, comment='使用的AI提供商'),

        # 对话统计
        sa.Column('message_count', sa.Integer, nullable=False, server_default='0', comment='消息总数'),
        sa.Column('total_tokens_used', sa.Integer, nullable=True, comment='总token使用量'),
        sa.Column('estimated_cost', sa.Float, nullable=True, comment='估算成本(美元)'),

        # 对话上下文
        sa.Column('context_summary', sa.Text, nullable=True, comment='对话上下文摘要'),
        sa.Column('intent_classification', sa.String(50), nullable=True, comment='对话意图分类'),

        # 对话状态
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true', comment='是否为活跃对话'),
        sa.Column('is_archived', sa.Boolean, nullable=False, server_default='false', comment='是否已归档'),

        # 时间戳
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='更新时间'),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True, comment='最后一条消息时间'),
    )

    # 创建conversations表索引
    op.create_index('ix_conversations_id', 'conversations', ['id'])
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # 创建health_data表
    op.create_table(
        'health_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID'),

        # 数据类型和来源
        sa.Column('data_type', sa.String(50), nullable=False, comment='数据类型'),
        sa.Column('source', sa.String(50), nullable=False, comment='数据来源'),

        # 数据值
        sa.Column('value', sa.Float, nullable=False, comment='数据值'),
        sa.Column('unit', sa.String(20), nullable=True, comment='单位'),

        # 加密数据
        sa.Column('encrypted_data', sa.Text, nullable=True, comment='加密的原始数据'),

        # 元数据
        sa.Column('metadata', postgresql.JSONB, nullable=True, comment='额外元数据'),

        # 数据采集时间
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='数据采集时间'),

        # 数据同步信息
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True, comment='数据同步时间'),
        sa.Column('external_id', sa.String(255), nullable=True, comment='外部系统ID'),

        # 数据质量
        sa.Column('quality_score', sa.Float, nullable=True, comment='数据质量评分(0-1)'),
        sa.Column('is_anomaly', sa.Boolean, nullable=False, server_default='false', comment='是否为异常值'),

        # 时间戳
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False, comment='更新时间'),
    )

    # 创建health_data表索引
    op.create_index('ix_health_data_id', 'health_data', ['id'])
    op.create_index('ix_health_data_user_id', 'health_data', ['user_id'])
    op.create_index('ix_health_data_data_type', 'health_data', ['data_type'])
    op.create_index('ix_health_data_recorded_at', 'health_data', ['recorded_at'])
    op.create_index('ix_health_data_user_type_recorded', 'health_data', ['user_id', 'data_type', 'recorded_at'])
    op.create_index('ix_health_data_user_recorded', 'health_data', ['user_id', 'recorded_at'])
    op.create_index('ix_health_data_external_id', 'health_data', ['external_id'])


def downgrade() -> None:
    """
    删除所有表
    """
    op.drop_index('ix_health_data_external_id', table_name='health_data')
    op.drop_index('ix_health_data_user_recorded', table_name='health_data')
    op.drop_index('ix_health_data_user_type_recorded', table_name='health_data')
    op.drop_index('ix_health_data_recorded_at', table_name='health_data')
    op.drop_index('ix_health_data_data_type', table_name='health_data')
    op.drop_index('ix_health_data_user_id', table_name='health_data')
    op.drop_index('ix_health_data_id', table_name='health_data')
    op.drop_table('health_data')

    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_id', table_name='conversations')
    op.drop_table('conversations')

    op.drop_index('ix_users_phone_number', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')

    # 删除枚举类型
    coach_type_enum = postgresql.ENUM(name='coach_type')
    coach_type_enum.drop(op.get_bind(), checkfirst=True)
