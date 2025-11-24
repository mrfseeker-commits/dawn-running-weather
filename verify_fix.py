import sys
import os
from app import app, db, User, SavedLocation

def verify_fix():
    print("Starting verification...")
    
    with app.app_context():
        # 1. Create a test user
        user = User.query.filter_by(username='test_verifier').first()
        if not user:
            user = User(username='test_verifier')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            print("Created test user.")
        else:
            print("Test user already exists.")
            
        # 2. Clean up previous test data
        SavedLocation.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        print("Cleaned up previous test locations.")
        
        # 3. Add first location
        loc1 = SavedLocation(
            user_id=user.id,
            region_name="Test Loc 1",
            region_code="07200580", # Jagok-dong
            lat=37.4,
            lng=127.1
        )
        db.session.add(loc1)
        db.session.commit()
        print("Added first location (07200580).")
        
        # 4. Add second location (same code)
        try:
            loc2 = SavedLocation(
                user_id=user.id,
                region_name="Test Loc 2",
                region_code="07200580", # Same code
                lat=37.5,
                lng=127.2
            )
            db.session.add(loc2)
            db.session.commit()
            print("Added second location (07200580) - SUCCESS!")
        except Exception as e:
            print(f"Failed to add second location: {e}")
            return False
            
        # 5. Verify count
        count = SavedLocation.query.filter_by(user_id=user.id).count()
        if count == 2:
            print(f"Verification PASSED: {count} locations saved.")
            return True
        else:
            print(f"Verification FAILED: Expected 2 locations, found {count}.")
            return False

if __name__ == "__main__":
    success = verify_fix()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
