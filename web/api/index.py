import os
import uuid
from dataclasses import dataclass
from typing import Optional

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types, text, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
  pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL',
                                                       "postgresql://cncld_web:ur_cncld@192.168.0.67:5432/cncld")
db = SQLAlchemy(app, model_class=Base)



@dataclass
class Item(Base):
    __tablename__ = "the_list"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(unique=True)
    confidence: Mapped[float] = mapped_column(types.Float)
    canceled: Mapped[bool] = mapped_column(types.Boolean)
    rationale: Mapped[str] = mapped_column(types.String)
    penance: Mapped[Optional[str]] = mapped_column(types.String, nullable=True)
    dimension: Mapped[str] = mapped_column(types.String)


@app.route("/api/<string:dims>/list/<string:item>")
def list_endpoint(dims, item):
    app.logger.info(f"Getting List for Search: {item}")
    stmt = db.select(Item).where(Item.title.ilike(f"{item}%"))
    items = list(db.session.execute(stmt).scalars())

    results = []
    for row in items:
        app.logger.info(row)
        row_hash = {key: value for key, value in row.__dict__.items() if '_' not in key}

        results.append(row_hash)
    app.logger.info(f"Found {len(results)} Items")

    response = jsonify({"results": results})
    app.logger.info(f"Response: {response.data}")
    return response


@app.route("/api/<string:dims>/random/cancel")
def random_endpoint(dims):
    stmt = db.select(Item).where(Item.canceled == True and Item.dimension == dims).order_by(func.random())
    item = db.session.execute(stmt).scalar()

    return jsonify({"result": {key: value for key, value in item.__dict__.items() if '_' not in key}})


if __name__ == "__main__":
    app.run(debug=True)