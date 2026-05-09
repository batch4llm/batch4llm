import { Modal } from "../Modal/Modal.tsx";

type Props = {
    isOpen: boolean;
    onClose: () => void;
};

export function PromptModal({ isOpen, onClose }: Props) {
    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Prompt Modal</h3>
            <p>Placeholder content for PromptModal</p>
        </Modal>
    );
}
