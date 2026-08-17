import { useEffect, useState, type FormEvent } from "react";
import { Plus, Trash2, Car, Calendar } from "lucide-react";
import { createCar, deleteCar, listCars } from "../api/cars";
import type { Car as CarType } from "../types";
import { PageHeader } from "../components/ui/PageHeader";
import { Spinner } from "../components/ui/Spinner";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { useToast } from "../context/ToastContext";

const CATEGORIES = ["Sedan", "SUV", "Coupe", "Pickup", "Wagon", "Convertible", "Hatchback"];

export function CarsPage() {
  const { toast } = useToast();
  const [cars, setCars] = useState<CarType[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<CarType | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [name, setName] = useState("");
  const [year, setYear] = useState("2020");
  const [makeId, setMakeId] = useState("1");
  const [modelName, setModelName] = useState("");
  const [category, setCategory] = useState("Sedan");

  const loadCars = async () => {
    setLoading(true);
    try {
      const data = await listCars(20);
      setCars(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to load cars", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCars();
  }, []);

  const resetForm = () => {
    setName("");
    setModelName("");
    setYear("2020");
    setMakeId("1");
    setCategory("Sedan");
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createCar({
        name,
        year: Number(year),
        make_id: Number(makeId),
        car_model_name: modelName,
        category: category || undefined,
      });
      toast("Car added successfully!", "success");
      setShowModal(false);
      resetForm();
      await loadCars();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to create car", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteCar(deleteTarget.id);
      toast("Car deleted", "success");
      setDeleteTarget(null);
      await loadCars();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to delete", "error");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Cars"
        description={`${total} car${total !== 1 ? "s" : ""} registered to your account`}
        action={
          <button onClick={() => setShowModal(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Add car
          </button>
        }
      />

      {loading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : cars.length === 0 ? (
        <EmptyState
          icon={Car}
          title="No cars yet"
          description="Register your first vehicle to keep track of it alongside the synced reports."
          action={
            <button onClick={() => setShowModal(true)} className="btn-primary">
              <Plus className="h-4 w-4" /> Add your first car
            </button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cars.map((car) => (
            <div key={car.id} className="card group p-5 transition hover:shadow-elevated">
              <div className="mb-4 flex items-start justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-100 text-surface-800 transition group-hover:bg-brand-600 group-hover:text-white">
                  <Car className="h-6 w-6" />
                </div>
                <button
                  onClick={() => setDeleteTarget(car)}
                  className="rounded-lg p-2 text-surface-800/30 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <h3 className="font-display text-lg font-bold">{car.name}</h3>
              <p className="text-sm text-brand-600">
                {car.car_model.make.name} {car.car_model.name}
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-bold text-brand-700">
                  {car.year}
                </span>
                {car.category && (
                  <span className="rounded-full bg-surface-100 px-2.5 py-1 text-xs font-medium text-surface-800">
                    {car.category}
                  </span>
                )}
              </div>
              <div className="mt-3 flex items-center gap-1.5 text-xs text-surface-800/40">
                <Calendar className="h-3.5 w-3.5" />
                Added {new Date(car.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add new car">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">Display name</label>
            <input className="input-field" value={name} onChange={(e) => setName(e.target.value)} required placeholder="My Toyota" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Model</label>
              <input className="input-field" value={modelName} onChange={(e) => setModelName(e.target.value)} required placeholder="Corolla" />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Year</label>
              <input type="number" className="input-field" value={year} onChange={(e) => setYear(e.target.value)} required min={1990} max={2026} />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Make ID</label>
              <input type="number" className="input-field" value={makeId} onChange={(e) => setMakeId(e.target.value)} required min={1} />
              <p className="mt-1 text-xs text-surface-800/50">From synced data (e.g. 1 = first make)</p>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Category</label>
              <select className="input-field" value={category} onChange={(e) => setCategory(e.target.value)}>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <button type="submit" className="btn-primary flex-1" disabled={submitting}>
              {submitting ? <Spinner size="sm" className="text-white" /> : "Save car"}
            </button>
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Delete car">
        <p className="text-sm text-surface-800/70">
          Are you sure you want to delete <strong>{deleteTarget?.name}</strong>? This cannot be undone.
        </p>
        <div className="mt-6 flex gap-2">
          <button onClick={handleDelete} className="btn-primary flex-1 bg-red-600 hover:bg-red-700">
            Delete
          </button>
          <button onClick={() => setDeleteTarget(null)} className="btn-secondary">
            Cancel
          </button>
        </div>
      </Modal>
    </div>
  );
}
