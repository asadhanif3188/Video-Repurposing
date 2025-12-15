from app.models.content import Post

class PublishingService:
    @staticmethod
    def publish_to_twitter(post: Post):
        """
        Stub for publishing to Twitter.
        """
        print(f"[{post.platform.upper()}] Publishing post {post.id}: {post.text}")
        # In future: Integration with Twitter API
        return True

    @staticmethod
    def publish_to_linkedin(post: Post):
        """
        Stub for publishing to LinkedIn.
        """
        print(f"[{post.platform.upper()}] Publishing post {post.id}: {post.text}")
        # In future: Integration with LinkedIn API
        return True
