"""Seed idempotente de categorías y subcategorías de changas.

Uso:
    python -m app.db.seed

Es idempotente: si una categoría ya existe (por nombre) no se duplica, y se
agregan solo las subcategorías que falten.
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.category import Categoria, SubCategoria

# Catálogo de categorías → subcategorías (changas típicas en Argentina).
CATALOGO: dict[str, list[str]] = {
    "Hogar y Reparaciones": [
        "Plomería",
        "Electricidad",
        "Gas",
        "Albañilería",
        "Pintura",
        "Carpintería",
        "Cerrajería",
        "Aire acondicionado",
    ],
    "Limpieza": [
        "Limpieza de hogar",
        "Limpieza de oficinas",
        "Limpieza de fin de obra",
        "Lavado de alfombras y tapizados",
    ],
    "Jardinería y Exteriores": [
        "Corte de césped",
        "Poda de árboles",
        "Diseño de jardines",
        "Pileta y mantenimiento",
    ],
    "Mudanzas y Fletes": [
        "Fletes",
        "Mudanzas",
        "Armado de muebles",
    ],
    "Tecnología": [
        "Reparación de PC",
        "Reparación de celulares",
        "Redes y WiFi",
        "Soporte técnico a domicilio",
    ],
    "Belleza y Bienestar": [
        "Peluquería",
        "Manicura y pedicura",
        "Masajes",
        "Maquillaje",
    ],
    "Clases Particulares": [
        "Matemática",
        "Idiomas",
        "Música",
        "Apoyo escolar",
        "Programación",
    ],
    "Eventos": [
        "Catering",
        "Fotografía",
        "DJ y sonido",
        "Animación infantil",
    ],
    "Mascotas": [
        "Paseo de perros",
        "Peluquería canina",
        "Cuidado de mascotas",
        "Adiestramiento",
    ],
    "Salud y Cuidados": [
        "Enfermería a domicilio",
        "Acompañante terapéutico",
        "Cuidado de adultos mayores",
        "Niñera",
    ],
}


def seed_categorias(db: Session) -> tuple[int, int]:
    """Inserta las categorías/subcategorías que falten. Devuelve (cats, subcats) creadas."""
    cats_creadas = 0
    subcats_creadas = 0

    for nombre_cat, subcats in CATALOGO.items():
        categoria = db.query(Categoria).filter(Categoria.nombre == nombre_cat).first()
        if categoria is None:
            categoria = Categoria(nombre=nombre_cat)
            db.add(categoria)
            db.flush()  # necesitamos el id para las subcategorías
            cats_creadas += 1

        existentes = {
            s.nombre
            for s in db.query(SubCategoria).filter(
                SubCategoria.categoria_id == categoria.id
            )
        }
        for nombre_sub in subcats:
            if nombre_sub not in existentes:
                db.add(SubCategoria(nombre=nombre_sub, categoria_id=categoria.id))
                subcats_creadas += 1

    db.commit()
    return cats_creadas, subcats_creadas


def main() -> None:
    db = SessionLocal()
    try:
        cats, subcats = seed_categorias(db)
        print(f"Seed completo: {cats} categorías y {subcats} subcategorías nuevas.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
