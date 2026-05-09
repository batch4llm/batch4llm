import { useEffect, useState } from "react";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { type Endpoint } from "../../types/Endpoint.ts";
import { AddEndpointModal } from "../../components/AddEndpointModal/AddEndpointModal.tsx";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import { EndpointCard } from "../../components/EndpointCard/EndpointCard.tsx";
import { AddCard } from "../../components/AddCard/AddCard.tsx";
import styles from "./EndpointsPage.module.css";

export default function EndpointsPage() {
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        EndpointsAPI.getAll().then(setEndpoints);
    }, []);

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
                    <EndpointCard key={ep.id} endpoint={ep} />
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
        </section>
    );
}
