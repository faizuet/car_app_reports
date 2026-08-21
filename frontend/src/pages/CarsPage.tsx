import { useEffect, useState, type FormEvent } from "react";
import { Plus, Trash2, Car, Calendar, Pencil, ChevronRight } from "lucide-react";
import { createCar, deleteCar, listCars, updateCar } from "../api/cars";
import { listMakes, listModelsForMake } from "../api/makes";
import type { Car as CarType, Make, CarModel } from "../types";
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
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingCar, setEditingCar] = useState<CarType | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<CarType | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [makes, setMakes] = useState<Make[]>([]);
  const [models, setModels] = useState<CarModel[]>([]);
  const [loadingMakes, setLoadingMakes] = useState(false);

  const [name, setName] = useState("");
  const [year, setYear] = useState("2020");
  const [makeId, setMakeId] = useState("");
  const [modelName, setModelName] = useState("");
  const [category, setCategory] = useState("Sedan");

  const loadCars = async (cursor?: number, append = false) => {
    if (append) setLoadingMore(true);
    else setLoading(true);

    try {
      const data = await listCars(20, cursor);
      setTotal(data.total);
      setNextCursor(data.next_cursor);
      setCars((prev) => (append ? [...prev, ...data.items] : data.items));
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to load cars", "error");
      if (!append) setCars([]);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    loadCars();
  }, []);

  const loadMakeOptions = async (preferredMakeId?: number) => {
    setLoadingMakes(true);
    try {
      const data = await listMakes();
      setMakes(data);
      const selectedId = preferredMakeId ?? data[0]?.id;
      if (selectedId) {
        setMakeId(String(selectedId));
        const modelData = await listModelsForMake(selectedId);
        setModels(modelData);
      }
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to load makes", "error");
    } finally {
      setLoadingMakes(false);
    }
  };

  const handleMakeChange = async (newMakeId: string) => {
    setMakeId(newMakeId);
    setModelName("");
    if (!newMakeId) {
      setModels([]);
      return;
    }
    try {
      const modelData = await listModelsForMake(Number(newMakeId));
      setModels(modelData);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to load models", "error");
      setModels([]);
    }
  };

  const resetForm = () => {
    setName("");
    setModelName("");
    setYear("2020");
    setMakeId("");
    setCategory("Sedan");
    setModels([]);
    setEditingCar(null);
  };

  const openCreateModal = () => {
    resetForm();
    setShowModal(true);
    loadMakeOptions();
  };

  const openEditModal = (car: CarType) => {
    setEditingCar(car);
    setName(car.name);
    setYear(String(car.year));
    setModelName(car.car_model.name);
    setCategory(car.category || "Sedan");
    setShowModal(true);
    loadMakeOptions(car.car_model.make.id);
  };

  const closeModal = () => {
    setShowModal(false);
    resetForm();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!makeId) {
      toast("Please select a make", "error");
      return;
    }

    setSubmitting(true);
    const payload = {
      name,
      year: Number(year),
      make_id: Number(makeId),
      car_model_name: modelName,
      category: category || undefined,
    };

    try {
      if (editingCar) {
        await updateCar(editingCar.id, payload);
        toast("Car updated successfully!", "success");
      } else {
        await createCar(payload);
        toast("Car added successfully!", "success");
      }
      closeModal();
      await loadCars();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save car", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteCar(deleteTarget.id);
      toast("Car deleted", "success");
      setDeleteTarget(null);
      await loadCars();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to delete", "error");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Cars"
        description={`${total} car${total !== 1 ? "s" : ""} registered to your account`}
        action={
          <button onClick={openCreateModal} className="btn-primary">
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
            <button onClick={openCreateModal} className="btn-primary">
              <Plus className="h-4 w-4" /> Add your first car
            </button>
          }
        />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cars.map((car) => (
              <div key={car.id} className="card group p-5 transition hover:shadow-elevated">
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-100 text-surface-800 transition group-hover:bg-brand-600 group-hover:text-white">
                    <Car className="h-6 w-6" />
                  </div>
                  <div className="flex gap-1 opacity-0 transition group-hover:opacity-100">
                    <button
                      onClick={() => openEditModal(car)}
                      className="rounded-lg p-2 text-surface-800/30 hover:bg-brand-50 hover:text-brand-600"
                      title="Edit"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setDeleteTarget(car)}
                      className="rounded-lg p-2 text-surface-800/30 hover:bg-red-50 hover:text-red-500"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
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

          {nextCursor && (
            <div className="flex justify-center pt-2">
              <button
                onClick={() => loadCars(nextCursor, true)}
                disabled={loadingMore}
                className="btn-secondary min-w-[140px]"
              >
                {loadingMore ? <Spinner size="sm" /> : (
                  <>Load more <ChevronRight className="h-4 w-4" /></>
                )}
              </button>
            </div>
          )}
        </>
      )}

      <Modal
        open={showModal}
        onClose={closeModal}
        title={editingCar ? "Edit car" : "Add new car"}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">Display name</label>
            <input
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="My Toyota"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Make</label>
              {loadingMakes ? (
                <div className="flex h-10 items-center"><Spinner size="sm" /></div>
              ) : (
                <select
                  className="input-field"
                  value={makeId}
                  onChange={(e) => handleMakeChange(e.target.value)}
                  required
                >
                  <option value="">Select make</option>
                  {makes.map((make) => (
                    <option key={make.id} value={make.id}>{make.name}</option>
                  ))}
                </select>
              )}
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium">Model</label>
              <input
                className="input-field"
                list="car-models"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                required
                placeholder="Corolla"
              />
              <datalist id="car-models">
                {models.map((model) => (
                  <option key={model.id} value={model.name} />
                ))}
              </datalist>
              <p className="mt-1 text-xs text-surface-800/50">Pick from list or type a new model name</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-sm font-medium">Year</label>
              <input
                type="number"
                className="input-field"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                required
                min={1990}
                max={2026}
              />
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
            <button type="submit" className="btn-primary flex-1" disabled={submitting || loadingMakes}>
              {submitting ? <Spinner size="sm" className="text-white" /> : editingCar ? "Save changes" : "Save car"}
            </button>
            <button type="button" onClick={closeModal} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </Modal>

      <Modal open={!!deleteTarget} onClose={() => !deleting && setDeleteTarget(null)} title="Delete car">
        <p className="text-sm text-surface-800/70">
          Are you sure you want to delete <strong>{deleteTarget?.name}</strong>? This cannot be undone.
        </p>
        <div className="mt-6 flex gap-2">
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="btn-primary flex-1 bg-red-600 hover:bg-red-700"
          >
            {deleting ? <Spinner size="sm" className="text-white" /> : "Delete"}
          </button>
          <button onClick={() => setDeleteTarget(null)} disabled={deleting} className="btn-secondary">
            Cancel
          </button>
        </div>
      </Modal>
    </div>
  );
}
