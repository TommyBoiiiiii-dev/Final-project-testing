# Smart Nutrition

A small local nutrition-label library. Enter the values from a food label and the app stores them in SQLite, then displays the foods you have saved.

## Run it

1. Install Python 3.9 or newer.
2. From this folder, run:

```powershell
python nutrition_app.py
```

3. Open <http://127.0.0.1:8000> in your browser.
4. Stop the server with `Ctrl+C`.

The first run creates `nutrition.db` automatically. It is intentionally ignored by Git because it is local user data.

## API

- `GET /api/foods` returns all saved food labels.
- `POST /api/foods` creates a food label. Required fields are `name` and `serving_size`.

The database stores calories, kJ energy, fat, saturated fat, carbohydrate, sugars, fibre, protein, sodium, salt, serving details, barcode, brand, and notes.

## Next sensible additions

- Edit and delete saved foods.
- Daily meal and portion tracking using the saved foods.
- User accounts and encrypted cloud sync.
- Barcode lookup through a food database API after the local workflow is stable.
