from app import app, db, SavedLocation

def inspect_locations():
    with app.app_context():
        locations = SavedLocation.query.all()
        print(f"Total Saved Locations: {len(locations)}")
        print("-" * 60)
        print(f"{'ID':<5} {'Region Name':<30} {'Region Code':<15} {'Lat':<10} {'Lng':<10}")
        print("-" * 60)
        for loc in locations:
            print(f"{loc.id:<5} {loc.region_name:<30} {loc.region_code:<15} {loc.lat:<10.4f} {loc.lng:<10.4f}")
        print("-" * 60)

if __name__ == "__main__":
    inspect_locations()
