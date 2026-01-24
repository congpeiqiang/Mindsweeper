# 数据库初始化脚本

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config.settings import settings
from app.schema import Base


def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)

    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )

    try:
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")

        # 创建所有表
        print("\n创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功")

        # 创建索引
        print("\n创建数据库索引...")
        with engine.connect() as conn:
            # 创建额外的索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_documents_kb_file ON documents(kb_id, file_id);",
                "CREATE INDEX IF NOT EXISTS idx_active_files ON files(kb_id) WHERE deleted_at IS NULL;",
            ]
            for idx in indexes:
                try:
                    conn.execute(text(idx))
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠ 索引创建失败: {e}")

        print("✓ 数据库索引创建成功")

        print("\n" + "=" * 50)
        print("✓ 数据库初始化完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    init_database()
