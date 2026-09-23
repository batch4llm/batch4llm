import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { EndpointsAPI } from "../../api/endpoints.ts";
import type { Endpoint } from "../../types/Endpoint.ts";
import { PROVIDERS } from "../../config/providers.ts";
import { ProviderSelectView } from "./views/ProviderSelectView.tsx";
import { ProviderFormView, type SubmitStatus } from "./views/ProviderFormView.tsx";
import type { Selected, Step } from "./types.ts";
import styles from "./AddEndpointModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (endpoint: Endpoint) => void;
};

type FormState = {
    step: Step;
    selected: Selected | null;
    name: string;
    token: string;
    customProvider: string;
    customClient: string;
    customUrl: string;
    status: SubmitStatus;
    error: string | null;
};

function initialFormState(): FormState {
    return {
        step: "select",
        selected: null,
        name: "",
        token: "",
        customProvider: "Self hosted",
        customClient: "openai",
        customUrl: "",
        status: "idle",
        error: null,
    };
}

export function AddEndpointModal({ isOpen, onClose, onCreated }: Props) {
    const [form, setForm] = useState<FormState>(initialFormState);

    // Reset the wizard back to the first step whenever it's (re-)opened,
    // without wiping fields the user is still editing while it's open.
    const [wasOpen, setWasOpen] = useState(isOpen);
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) setForm(initialFormState());
    }

    function update(patch: Partial<FormState>) {
        setForm((prev) => ({ ...prev, ...patch }));
    }

    function buildPayload(): Record<string, string> {
        if (form.selected === "custom") {
            return {
                name: form.name,
                client: form.customClient,
                provider: form.customProvider,
                ...(form.customUrl ? { url: form.customUrl } : {}),
                ...(form.token ? { token: form.token } : {}),
            };
        }
        const prov = PROVIDERS.find((p) => p.id === form.selected);
        return {
            name: form.name,
            client: prov?.client ?? "",
            provider: prov?.provider ?? "",
            ...(prov?.url ? { url: prov.url } : {}),
            ...(form.token ? { token: form.token } : {}),
        };
    }

    const isCustom = form.selected === "custom";
    const isValid = isCustom
        ? form.name.trim().length >= 3 && form.customProvider.trim().length >= 1 && form.customClient.trim().length >= 1
        : form.selected !== null && form.name.trim().length >= 3 && form.token.trim().length >= 3;

    function handleSubmit() {
        if (!isValid || form.status !== "idle") return;
        update({ status: "testing", error: null });
        const payload = buildPayload();
        EndpointsAPI.test(payload)
            .then((testResult) => {
                if (!testResult.success) {
                    update({ status: "idle", error: testResult.error || "Connection failed." });
                    return;
                }
                update({ status: "creating" });
                return EndpointsAPI.create(payload).then((created) => {
                    onCreated(created);
                    onClose();
                });
            })
            .catch((err) => {
                update({ status: "idle", error: err?.response?.data?.detail || String(err) });
            });
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} className={styles.modal}>
            {form.step === "select" ? (
                <ProviderSelectView
                    onSelect={(selected) => update({
                        step: "form",
                        selected,
                        name: "",
                        token: "",
                        customProvider: "Self hosted",
                        customClient: "openai",
                        customUrl: "",
                        status: "idle",
                        error: null,
                    })}
                />
            ) : (
                <ProviderFormView
                    selected={form.selected as Selected}
                    name={form.name}
                    onSetName={(name) => update({ name })}
                    token={form.token}
                    onSetToken={(token) => update({ token })}
                    customProvider={form.customProvider}
                    onSetCustomProvider={(customProvider) => update({ customProvider })}
                    customClient={form.customClient}
                    onSetCustomClient={(customClient) => update({ customClient })}
                    customUrl={form.customUrl}
                    onSetCustomUrl={(customUrl) => update({ customUrl })}
                    status={form.status}
                    error={form.error}
                    isValid={isValid}
                    onBack={() => update({ step: "select", error: null, status: "idle" })}
                    onSubmit={handleSubmit}
                />
            )}
        </Modal>
    );
}
