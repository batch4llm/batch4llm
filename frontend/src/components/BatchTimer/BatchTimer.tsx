import { useSyncExternalStore } from "react";

type BatchTimerProps = {
    startTime: string;
    stopTime?: string;
};

export function BatchTimer({ startTime, stopTime }: BatchTimerProps) {
    const liveNow = useSyncExternalStore(
        (cb) => {
            if (stopTime) return () => {};
            const id = setInterval(cb, 1000);
            return () => clearInterval(id);
        },
        () => Date.now()
    );

    const startDate = new Date(startTime).getTime();
    const end = stopTime
        ? new Date(stopTime).getTime()
        : liveNow;

    const seconds = Math.max(0, Math.floor((end - startDate) / 1000));

    return <span>{formatTime(seconds)}</span>;
}


function formatTime(totalSeconds: number) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    return `${h.toString().padStart(2, "0")}:${m
        .toString()
        .padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}
