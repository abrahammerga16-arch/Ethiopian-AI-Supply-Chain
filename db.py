"""
utils/db.py  —  Local SQLite database (swap for Supabase later)
"""
import sqlite3, os, hashlib, uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "trade_hub.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        pw_hash     TEXT NOT NULL,
        role        TEXT NOT NULL DEFAULT 'Customer',
        region      TEXT,
        phone       TEXT,
        is_verified INTEGER DEFAULT 0,
        created_at  TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        id          TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        title       TEXT NOT NULL,
        sector      TEXT,
        product     TEXT,
        quantity    REAL,
        unit        TEXT,
        price       REAL,
        quality     TEXT,
        region      TEXT,
        description TEXT,
        can_deliver INTEGER DEFAULT 0,
        status      TEXT DEFAULT 'Active',
        created_at  TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        id          TEXT PRIMARY KEY,
        product_id  TEXT NOT NULL,
        buyer_id    TEXT NOT NULL,
        seller_id   TEXT NOT NULL,
        quantity    REAL,
        total_price REAL,
        status      TEXT DEFAULT 'Pending',
        created_at  TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(buyer_id)   REFERENCES users(id),
        FOREIGN KEY(seller_id)  REFERENCES users(id)
    );
    """)

    # Demo accounts
    _seed_demo_users(conn, c)
    conn.commit()
    conn.close()


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _seed_demo_users(conn, c):
    demos = [
        (str(uuid.uuid4()), "Abebe Girma",  "producer@test.com", _hash("test123"), "Producer",  "Oromia",      "+251911000001"),
        (str(uuid.uuid4()), "Tigist Alemu", "merchant@test.com", _hash("test123"), "Merchant",  "Addis Ababa", "+251911000002"),
        (str(uuid.uuid4()), "Dawit Bekele", "customer@test.com", _hash("test123"), "Customer",  "Amhara",      "+251911000003"),
        (str(uuid.uuid4()), "Sara Admin",   "admin@test.com",    _hash("test123"), "Admin",     "Addis Ababa", "+251911000004"),
    ]
    for d in demos:
        try:
            c.execute(
                "INSERT INTO users (id,name,email,pw_hash,role,region,phone,is_verified,created_at) VALUES (?,?,?,?,?,?,?,1,?)",
                (*d, datetime.now().isoformat()),
            )
        except sqlite3.IntegrityError:
            pass  # already seeded

    # Seed some demo products
    _seed_demo_products(conn, c)


def _seed_demo_products(conn, c):
    c.execute("SELECT COUNT(*) as n FROM products")
    if c.fetchone()["n"] > 0:
        return
    c.execute("SELECT id FROM users WHERE role='Producer' LIMIT 1")
    row = c.fetchone()
    if not row:
        return
    uid = row["id"]
    items = [
        (str(uuid.uuid4()), uid, "Premium Teff — 500 kg", "Agriculture", "Teff", 500, "kg", 45, "A", "Oromia", "Freshly harvested white teff, Grade A", 1),
        (str(uuid.uuid4()), uid, "Organic Coffee Beans", "Agriculture", "Coffee", 200, "kg", 320, "A", "Oromia", "Single-origin Jimma coffee, sun-dried", 1),
        (str(uuid.uuid4()), uid, "Handwoven Cotton Shawl", "Handicrafts", "Textiles", 50, "pcs", 180, "B", "Oromia", "Traditional Ethiopian cotton shawls", 0),
        (str(uuid.uuid4()), uid, "Maize (Corn) — 1 ton", "Agriculture", "Maize", 1000, "kg", 22, "B", "Oromia", "Yellow maize, recently harvested", 1),
    ]
    for item in items:
        try:
            c.execute("""
                INSERT INTO products (id,user_id,title,sector,product,quantity,unit,price,quality,region,description,can_deliver,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (*item, datetime.now().isoformat()))
        except Exception:
            pass


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(name, email, pw, role, region, phone):
    conn = get_conn()
    uid = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO users (id,name,email,pw_hash,role,region,phone,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (uid, name, email, _hash(pw), role, region, phone, datetime.now().isoformat()),
        )
        conn.commit()
        return True, uid
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()


def get_products(region=None, sector=None, quality=None, search=None, user_id=None, status="Active"):
    conn = get_conn()
    q = """
        SELECT p.*, u.name as seller_name, u.phone as seller_phone, u.is_verified as seller_verified
        FROM products p JOIN users u ON p.user_id = u.id
        WHERE p.status = ?
    """
    params = [status]
    if region and region != "All":
        q += " AND p.region = ?"; params.append(region)
    if sector and sector != "All":
        q += " AND p.sector = ?"; params.append(sector)
    if quality and quality != "All":
        q += " AND p.quality = ?"; params.append(quality)
    if search:
        q += " AND (p.title LIKE ? OR p.description LIKE ?)"; params += [f"%{search}%", f"%{search}%"]
    if user_id:
        q += " AND p.user_id = ?"; params.append(user_id)
    q += " ORDER BY p.created_at DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_product(user_id, title, sector, product, quantity, unit, price, quality, region, description, can_deliver):
    conn = get_conn()
    pid = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO products (id,user_id,title,sector,product,quantity,unit,price,quality,region,description,can_deliver,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (pid, user_id, title, sector, product, quantity, unit, price, quality, region, description, int(can_deliver), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return pid


def delete_product(product_id, user_id):
    conn = get_conn()
    conn.execute("UPDATE products SET status='Deleted' WHERE id=? AND user_id=?", (product_id, user_id))
    conn.commit()
    conn.close()


def create_order(product_id, buyer_id, seller_id, quantity, total_price):
    conn = get_conn()
    oid = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO orders (id,product_id,buyer_id,seller_id,quantity,total_price,created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (oid, product_id, buyer_id, seller_id, quantity, total_price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return oid


def get_orders(user_id, as_buyer=True):
    conn = get_conn()
    field = "buyer_id" if as_buyer else "seller_id"
    rows = conn.execute(f"""
        SELECT o.*, p.title, p.unit, p.sector, u.name as counterpart_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON u.id = {'o.seller_id' if as_buyer else 'o.buyer_id'}
        WHERE o.{field} = ?
        ORDER BY o.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT id,name,email,role,region,is_verified,created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_profile(user_id, name, phone, region):
    conn = get_conn()
    conn.execute("UPDATE users SET name=?,phone=?,region=? WHERE id=?", (name, phone, region, user_id))
    conn.commit()
    conn.close()
