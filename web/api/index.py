import uuid

from dataclasses import dataclass
from typing import Optional

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
class Base(DeclarativeBase):
  pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] ="postgresql://cncld_web:ur_cncld@192.168.0.67:5432/cncld"
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


@app.route("/api/list")
@app.route("/api/list/<string:item>")
def list_endpoint(item=None):
    app.logger.info(f"Getting List for Search: {item}")
    if item:
        stmt = db.select(Item).where(Item.title.ilike(f"%{item}%"))
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
    else:
        return jsonify({"results": []})



if __name__ == "__main__":
    app.run(debug=True)