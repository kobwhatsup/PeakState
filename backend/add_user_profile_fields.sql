-- 添加用户画像字段到users表
-- 如果字段已存在则跳过

DO $$
BEGIN
    -- 添加age字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='age') THEN
        ALTER TABLE users ADD COLUMN age INTEGER NULL;
        RAISE NOTICE 'Added column: age';
    ELSE
        RAISE NOTICE 'Column age already exists, skipping';
    END IF;

    -- 添加gender字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='gender') THEN
        ALTER TABLE users ADD COLUMN gender VARCHAR(20) NULL;
        RAISE NOTICE 'Added column: gender';
    ELSE
        RAISE NOTICE 'Column gender already exists, skipping';
    END IF;

    -- 添加occupation字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='occupation') THEN
        ALTER TABLE users ADD COLUMN occupation VARCHAR(100) NULL;
        RAISE NOTICE 'Added column: occupation';
    ELSE
        RAISE NOTICE 'Column occupation already exists, skipping';
    END IF;

    -- 添加health_goals字段
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='health_goals') THEN
        ALTER TABLE users ADD COLUMN health_goals VARCHAR(500) NULL;
        RAISE NOTICE 'Added column: health_goals';
    ELSE
        RAISE NOTICE 'Column health_goals already exists, skipping';
    END IF;
END $$;

-- 添加列注释
COMMENT ON COLUMN users.age IS '年龄';
COMMENT ON COLUMN users.gender IS '性别(male/female/other/prefer_not_to_say)';
COMMENT ON COLUMN users.occupation IS '职业';
COMMENT ON COLUMN users.health_goals IS '健康目标(逗号分隔,如: improve_sleep,reduce_stress,increase_energy)';

-- 验证结果
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('age', 'gender', 'occupation', 'health_goals')
ORDER BY column_name;
