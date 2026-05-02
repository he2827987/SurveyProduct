import pymysql
import psycopg2
import json

CLOUD_PG = {
    'host': 'dpg-d7negmsvikkc73b7j52g-a.oregon-postgres.render.com',
    'port': 5432, 'database': 'survey_product_db',
    'user': 'survey_product_db_user',
    'password': '4zKQvRwdaCf6xBgirmw0pQQpCYCiboJH',
    'sslmode': 'require', 'connect_timeout': 60,
}

BOOL = {'is_active', 'is_public', 'is_required'}
MYSQL_RES = {'order', 'level', 'text', 'status', 'name', 'path'}
PG_RES = {'order', 'level', 'text', 'status', 'name', 'path', 'user'}

def c(col, v):
    if v is None: return None
    if isinstance(v, bytes): return v.decode('utf-8', errors='replace')
    if col in BOOL and isinstance(v, (int,)): return bool(v)
    if isinstance(v, (dict, list)): return json.dumps(v, ensure_ascii=False, default=str)
    return v

def read(mc, t, cols):
    es = [f'`{x}`' if x.lower() in MYSQL_RES else x for x in cols]
    mc.execute(f"SELECT {', '.join(es)} FROM `{t}` ORDER BY id")
    return mc.fetchall()

def ins(pg, t, cols, rows):
    if not rows:
        print(f"  {t}: 0", flush=True)
        return 0
    qcols = ['"{}"'.format(x) if x.lower() in PG_RES else x for x in cols]
    sql = f"INSERT INTO {t} ({', '.join(qcols)}) VALUES ({', '.join(['%s']*len(cols))})"
    ok = 0
    for row in rows:
        vals = [c(col, row[col]) for col in cols]
        try:
            cur = pg.cursor()
            cur.execute(sql, vals)
            pg.commit()
            ok += 1
        except Exception as e:
            pg.rollback()
            print(f"    FAIL id={row.get('id','?')}: {str(e)[:150]}", flush=True)
    print(f"  {t}: {ok}/{len(rows)}", flush=True)
    return ok

def main():
    print("=== MIGRATION ===\n", flush=True)

    mysql = pymysql.connect(host='localhost', user='root', password='', database='survey_db', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    mc = mysql.cursor()
    pg = psycopg2.connect(**CLOUD_PG)

    # FK already dropped. Just truncate and insert.
    print("[0] Truncating...", flush=True)
    cur = pg.cursor()
    for t in ['question_tags','survey_answers','survey_questions','organization_members','participants','questions','categories','departments','surveys','organizations','tags','users']:
        try: cur.execute(f"TRUNCATE TABLE {t} CASCADE")
        except: pass
    pg.commit()

    tables = [
        ('users', ['id','username','email','hashed_password','role','is_active','created_at','updated_at','manager_id','organization_id']),
        ('organizations', ['id','name','description','owner_id','is_active','is_public','created_at','updated_at']),
        ('categories', ['id','name','description','code','organization_id','parent_id','level','path','sort_order','is_active','created_by','created_at','updated_at']),
        ('tags', ['id','name','color','description','created_at','updated_at']),
        ('departments', ['id','name','code','description','organization_id','parent_id','level','is_active','created_at','updated_at']),
        ('participants', ['id','name','department_id','position','email','phone','organization_id','created_at','updated_at']),
        ('questions', ['id','text','type','owner_id','organization_id','category_id','options','min_score','max_score','is_required','order','usage_count','parent_question_id','trigger_options','created_at','updated_at']),
        ('surveys', ['id','title','description','status','created_by_user_id','organization_id','start_time','end_time','created_at','updated_at']),
        ('survey_questions', ['id','survey_id','question_id','order','created_at']),
        ('survey_answers', ['id','survey_id','user_id','participant_id','submitted_at','answers','total_score','department','position','organization_id','organization_name']),
        ('organization_members', ['id','organization_id','user_id','role','created_at','updated_at']),
    ]

    for i, (t, cols) in enumerate(tables, 1):
        print(f"[{i}/{len(tables)}] {t}...", flush=True)
        rows = read(mc, t, cols)
        ins(pg, t, cols, rows)

    # question_tags
    print(f"[{len(tables)+1}] question_tags...", flush=True)
    mc.execute("SELECT question_id, tag_id FROM `question_tags`")
    qt = mc.fetchall()
    if qt:
        sql = 'INSERT INTO question_tags (question_id, tag_id) VALUES (%s,%s)'
        ok = 0
        for r in qt:
            try:
                cur.execute(sql, [r['question_id'], r['tag_id']])
                pg.commit()
                ok += 1
            except:
                pg.rollback()
        print(f"  question_tags: {ok}/{len(qt)}", flush=True)

    # Restore FK constraints
    print("\n[FK] Restoring constraints...", flush=True)
    fks = [
        ('users', 'users_manager_id_fkey', 'manager_id', 'users', 'id'),
        ('users', 'users_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('organizations', 'organizations_owner_id_fkey', 'owner_id', 'users', 'id'),
        ('categories', 'categories_parent_id_fkey', 'parent_id', 'categories', 'id'),
        ('categories', 'categories_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('categories', 'categories_created_by_fkey', 'created_by', 'users', 'id'),
        ('departments', 'departments_parent_id_fkey', 'parent_id', 'departments', 'id'),
        ('departments', 'departments_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('participants', 'participants_department_id_fkey', 'department_id', 'departments', 'id'),
        ('participants', 'participants_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('questions', 'questions_parent_question_id_fkey', 'parent_question_id', 'questions', 'id'),
        ('questions', 'questions_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('questions', 'questions_owner_id_fkey', 'owner_id', 'users', 'id'),
        ('questions', 'questions_category_id_fkey', 'category_id', 'categories', 'id'),
        ('surveys', 'surveys_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('surveys', 'surveys_created_by_user_id_fkey', 'created_by_user_id', 'users', 'id'),
        ('survey_questions', 'survey_questions_question_id_fkey', 'question_id', 'questions', 'id'),
        ('survey_questions', 'survey_questions_survey_id_fkey', 'survey_id', 'surveys', 'id'),
        ('survey_answers', 'survey_answers_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('survey_answers', 'survey_answers_user_id_fkey', 'user_id', 'users', 'id'),
        ('survey_answers', 'survey_answers_participant_id_fkey', 'participant_id', 'participants', 'id'),
        ('survey_answers', 'survey_answers_survey_id_fkey', 'survey_id', 'surveys', 'id'),
        ('organization_members', 'organization_members_user_id_fkey', 'user_id', 'users', 'id'),
        ('organization_members', 'organization_members_organization_id_fkey', 'organization_id', 'organizations', 'id'),
        ('question_tags', 'question_tags_tag_id_fkey', 'tag_id', 'tags', 'id'),
        ('question_tags', 'question_tags_question_id_fkey', 'question_id', 'questions', 'id'),
    ]
    restored = 0
    for tbl, con, col, ref, ref_col in fks:
        try:
            cur.execute(f'ALTER TABLE {tbl} ADD CONSTRAINT {con} FOREIGN KEY ({col}) REFERENCES {ref}({ref_col})')
            restored += 1
        except Exception as e:
            print(f"  FAIL {tbl}.{con}: {str(e)[:100]}", flush=True)
    pg.commit()
    print(f"  Restored {restored}/{len(fks)} FK constraints.", flush=True)

    # Sequences
    print("\nUpdating sequences...", flush=True)
    cur.execute("SELECT t.relname FROM pg_class t JOIN pg_attribute a ON a.attrelid=t.oid JOIN pg_attrdef d ON d.adrelid=t.oid AND d.adnum=a.attnum WHERE t.relkind='r' AND t.relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public') AND a.attname='id'")
    for (tn,) in cur.fetchall():
        try: cur.execute(f"SELECT setval('{tn}_id_seq', (SELECT COALESCE(MAX(id),1) FROM {tn}))")
        except: pass
    pg.commit()

    # Verify
    print("\n=== VERIFICATION ===", flush=True)
    expected = {'users':11,'organizations':10,'categories':8,'tags':12,'departments':5,'participants':0,'questions':86,'surveys':11,'survey_questions':22,'survey_answers':116,'organization_members':5,'question_tags':4}
    all_ok = True
    for t, exp in expected.items():
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        act = cur.fetchone()[0]
        s = "OK" if act == exp else f"EXPECTED {exp}"
        if act != exp: all_ok = False
        print(f"  {t}: {act} {s}", flush=True)

    print(f"\n{'ALL OK!' if all_ok else 'ISSUES FOUND'}", flush=True)
    mc.close()
    mysql.close()
    pg.close()

if __name__ == '__main__':
    main()
