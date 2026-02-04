from datetime import datetime

class User:
    def __init__(self, name: str, display_name: str, email: str, bio: str, avatar_path: str, created_at: datetime, last_active_at:datetime):
        self.id = 0
        self.name = name
        self.display_name = display_name
        self.email = email
        self.bio = bio
        self.avatar_path = avatar_path
        self.created_at = created_at
        self.last_active_at = last_active_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'email': self.email,
            'bio': self.bio,
            'avatar_path': self.avatar_path,
            'created_at': self.created_at.isoformat(),
            'last_active_at': self.last_active_at.isoformat()
        }