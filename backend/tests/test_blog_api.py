"""
博客生成 API 测试
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestBlogAPI:
    """测试博客生成 API"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            yield client
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_generate_blog_missing_topic(self, client):
        """测试缺少 topic 参数"""
        response = client.post(
            '/api/blog/generate',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'topic' in data['error']
    
    def test_generate_blog_no_json(self, client):
        """测试没有 JSON 数据"""
        response = client.post('/api/blog/generate')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('services.blog_generator.blog_service.get_blog_service')
    def test_generate_blog_service_unavailable(self, mock_get_service, client):
        """测试服务不可用"""
        mock_get_service.return_value = None
        
        response = client.post(
            '/api/blog/generate',
            json={'topic': 'Test Topic'},
            content_type='application/json'
        )
        
        # 服务不可用时返回 500
        assert response.status_code == 500
    
    @pytest.mark.skip(reason="需要完整服务环境")
    def test_generate_blog_success(self, client):
        """测试成功创建任务"""
        response = client.post(
            '/api/blog/generate',
            json={
                'topic': 'LangGraph 入门',
                'article_type': 'tutorial',
                'target_audience': 'intermediate',
                'target_length': 'short'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'task_id' in data


class TestBlogSyncAPI:
    """测试同步博客生成 API"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        
        from app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            yield client
    
    def test_sync_generate_missing_topic(self, client):
        """测试同步生成缺少 topic"""
        response = client.post(
            '/api/blog/generate/sync',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
