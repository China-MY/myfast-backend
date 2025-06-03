from fastapi import Query


class PaginationParams:
    """
    分页查询参数
    """
    
    def __init__(
        self,
        page_num: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    ):
        self.page_num = page_num
        self.page_size = page_size 