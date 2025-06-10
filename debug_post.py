from app.db.session import SessionLocal
from app.models.post import SysPost

def main():
    """查询岗位表数据"""
    db = SessionLocal()
    try:
        posts = db.query(SysPost).all()
        if not posts:
            print("岗位表中没有数据")
        else:
            print(f"找到 {len(posts)} 条岗位记录:")
            for post in posts:
                print(f"ID: {post.post_id}, 名称: {post.post_name}, 编码: {post.post_code}, 状态: {post.status}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 