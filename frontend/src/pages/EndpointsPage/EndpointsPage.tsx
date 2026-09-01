import { useEffect, useState } from "react";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { type Endpoint } from "../../types/Endpoint.ts";
import { AddEndpointModal } from "../../components/AddEndpointModal/AddEndpointModal.tsx";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import { EndpointCard } from "../../components/EndpointCard/EndpointCard.tsx";
import { AddCard } from "../../components/AddCard/AddCard.tsx";
import { Modal } from "../../components/Modal/Modal.tsx";
import styles from "./EndpointsPage.module.css";

// ── Confirm Delete Modal ────────────────────────────────────────
type DeleteModalProps = {
    endpoint: Endpoint | null;
    onClose: () => void;
    onConfirm: (id: number) => void;
};

function ConfirmDeleteModal({ endpoint, onClose, onConfirm }: DeleteModalProps) {
    if (!endpoint) return null;
    return (
        <Modal isOpen onClose={onClose} className={styles.narrowModal}>
            <h3 className={styles.confirmTitle}>Delete endpoint?</h3>
            <p className={styles.confirmBody}>
                <strong>{endpoint.name}</strong> will be permanently removed. Batches that
                already used it keep showing its name, but this cannot be undone.
            </p>
            <div className={styles.confirmActions}>
                <button className={styles.btnSecondary} onClick={onClose}>Cancel</button>
                <button className={styles.btnDanger} onClick={() => { onConfirm(endpoint.id); onClose(); }}>Delete</button>
            </div>
        </Modal>
    );
}

export default function EndpointsPage() {
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleting, setDeleting] = useState<Endpoint | null>(null);

    useEffect(() => {
        EndpointsAPI.getAll().then(setEndpoints);
    }, []);

    function handleDelete(id: number) {
        EndpointsAPI.delete(id)
            .then(() => setEndpoints(prev => prev.filter(ep => ep.id !== id)))
            .catch((err) => {
                const detail = err?.response?.data?.detail;
                alert(detail || "Endpoint could not be deleted.");
            });
    }

    return (
        <section>
            <PageHeader
                title="Endpoints"
                subtitle="Connected AI providers your batches can route to. Tokens are stored encrypted and never returned to the browser after creation."
                count={endpoints.length}
                addLabel="Add Endpoint"
                onAdd={() => setIsModalOpen(true)}
            />

            <div className={styles.grid}>
                {endpoints.map(ep => (
                    <EndpointCard key={ep.id} endpoint={ep} onDelete={setDeleting} />
                ))}
                <AddCard label="Add Endpoint" onClick={() => setIsModalOpen(true)} />
            </div>

            <AddEndpointModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={(newEndpoint: Endpoint) =>
                    setEndpoints(prev => [...prev, newEndpoint])
                }
            />

            <ConfirmDeleteModal
                endpoint={deleting}
                onClose={() => setDeleting(null)}
                onConfirm={handleDelete}
            />
        </section>
    );
}
