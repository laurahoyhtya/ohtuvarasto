from flask import Flask, flash, redirect, render_template, request

from varasto import Varasto


class Warehouse:
    def __init__(self, name, capacity):
        self.name = name
        self.storage = Varasto(capacity)

    @property
    def capacity(self):
        return self.storage.tilavuus

    @property
    def stock(self):
        return self.storage.saldo

    @property
    def remaining_capacity(self):
        return self.storage.paljonko_mahtuu()


warehouses = {}
next_warehouse_id = 1


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "ohtuvarasto-development-key"

    def positive_whole_number(value):
        if value is None or not value.isdigit():
            return None
        number = int(value)
        return number if number > 0 else None

    def create_warehouse_from_form():
        global next_warehouse_id

        name = request.form.get("name", "").strip()
        capacity = positive_whole_number(request.form.get("capacity"))
        if not name:
            flash("Give the warehouse a name.")
        elif capacity is None:
            flash("Capacity must be a positive whole number.")
        else:
            warehouse_id = next_warehouse_id
            next_warehouse_id += 1
            warehouses[warehouse_id] = Warehouse(name, capacity)
            flash(f'Warehouse "{name}" created.')

    def adjust_goods(warehouse_id, action):
        warehouse = warehouses.get(warehouse_id)
        if warehouse is None:
            flash("Select a valid warehouse.")
            return

        quantity = positive_whole_number(
            request.form.get("quantity") or request.form.get("amount")
        )
        if quantity is None:
            flash("Quantity must be a positive whole number.")
        elif action == "add":
            if quantity > warehouse.remaining_capacity:
                flash("The goods do not fit in the remaining capacity.")
            else:
                warehouse.storage.lisaa_varastoon(quantity)
                flash(f'Added {quantity} goods to "{warehouse.name}".')
        else:
            if quantity > warehouse.stock:
                flash("Not enough goods in the warehouse.")
            else:
                warehouse.storage.ota_varastosta(quantity)
                flash(f'Removed {quantity} goods from "{warehouse.name}".')

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            action = request.form.get("action")
            if action == "create":
                create_warehouse_from_form()
                return redirect("/")

            if action in ("add", "remove"):
                try:
                    warehouse_id = int(request.form.get("warehouse_id"))
                except (TypeError, ValueError):
                    flash("Select a valid warehouse.")
                    return redirect("/")
                adjust_goods(warehouse_id, action)
                return redirect("/")

        return render_template("warehouses.html", warehouses=warehouses)

    @app.post("/warehouses")
    @app.post("/warehouses/create")
    @app.post("/create")
    def create_warehouse():
        create_warehouse_from_form()
        return redirect("/")

    @app.post("/warehouses/<int:warehouse_id>/add")
    @app.post("/add/<int:warehouse_id>")
    def add_goods(warehouse_id):
        adjust_goods(warehouse_id, "add")
        return redirect("/")

    @app.post("/warehouses/<int:warehouse_id>/remove")
    @app.post("/remove/<int:warehouse_id>")
    def remove_goods(warehouse_id):
        adjust_goods(warehouse_id, "remove")
        return redirect("/")

    app.warehouse_store = warehouses
    return app


app = create_app()
