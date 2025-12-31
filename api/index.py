import os
import uuid
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types, text, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
  pass

custom_static_path = Path(os.path.join(os.path.dirname(__file__), "../out")).resolve()

application = Flask(__name__, static_folder=custom_static_path, static_url_path='/')

DATABASE_URL =  os.environ.get('DATABASE_URL', "postgresql://cncld_web:ur_cncld@192.168.0.67:5432/cncld").replace("postgres://", "postgresql://")

application.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

db = SQLAlchemy(application, model_class=Base)



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


@application.route("/api/<string:dims>/list/<string:item>")
def list_endpoint(dims, item):
    application.logger.info(f"Getting List for Search: {item}")
    stmt = db.select(Item).where(Item.title.ilike(f"{item}%"))
    items = list(db.session.execute(stmt).scalars())

    results = []
    for row in items:
        application.logger.info(row)
        row_hash = {key: value for key, value in row.__dict__.items() if '_' not in key}

        results.append(row_hash)
    application.logger.info(f"Found {len(results)} Items")

    response = jsonify({"results": results})
    application.logger.info(f"Response: {response.data}")
    return response


@application.route("/api/<string:dims>/random/cancel")
def random_endpoint(dims):
    stmt = db.select(Item).where(Item.canceled == True and Item.dimension == dims).order_by(func.random())
    item = db.session.execute(stmt).scalar()

    return jsonify({"result": {key: value for key, value in item.__dict__.items() if '_' not in key}})


@application.route("/")
def index():
    return application.send_static_file("index.html")

__all__ = ["application"]

if __name__ == "__main__":
    app.run()