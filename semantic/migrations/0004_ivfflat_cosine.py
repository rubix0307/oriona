from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("semantic", "0003_remove_ingestarticleembedding_semantic_in_model_n_8aff49_idx_and_more"),
    ]
    operations = [
        migrations.RunSQL(
            """
            CREATE INDEX IF NOT EXISTS ingestarticleembedding_vector_ivfflat
            ON semantic_ingestarticleembedding
            USING ivfflat (vector vector_cosine_ops)
            WITH (lists = 100);
            """,
            """
            DROP INDEX IF EXISTS ingestarticleembedding_vector_ivfflat;
            """
        ),
        migrations.RunSQL("ANALYZE semantic_ingestarticleembedding;"),
    ]