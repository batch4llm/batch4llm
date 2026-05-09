import { Modal } from "../Modal/Modal.tsx";

type Props = {
    isOpen: boolean;
    onClose: () => void;
};

export function EndpointModal({ isOpen, onClose }: Props) {
    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Endpoint Modal</h3>
            <p>Placeholder content for EndpointModal</p>
        </Modal>
    );
}
