export function ReplayControls({
  isPlaying,
  speed,
  timestampMs,
  onPlayChange,
  onSpeedChange,
  onSeek,
  interactive = true,
  complete = false,
}: {
  isPlaying: boolean;
  speed: number;
  timestampMs: number;
  onPlayChange: (playing: boolean) => void;
  onSpeedChange: (speed: number) => void;
  onSeek: (timestampMs: number) => void;
  interactive?: boolean;
  complete?: boolean;
}) {
  const controlLabel = complete
    ? "Replay complete"
    : interactive
      ? isPlaying
        ? "Pause waveform replay"
        : "Resume waveform replay"
      : "Server-controlled replay";
  return (
    <div className="replay-controls" role="group" aria-label="Replay controls">
      <button
        className="play-button"
        type="button"
        onClick={() => onPlayChange(!isPlaying)}
        aria-label={controlLabel}
        disabled={!interactive || complete}
      >
        {complete ? "■" : isPlaying ? "Ⅱ" : "▶"}
      </button>
      <label>
        <span>Replay position</span>
        <input
          type="range"
          min={0}
          max={600000}
          step={10000}
          value={Math.min(timestampMs, 600000)}
          onChange={(event) => onSeek(Number(event.target.value))}
          disabled={!interactive || complete}
        />
      </label>
      <label className="speed-select">
        <span>Speed</span>
        <select
          value={speed}
          onChange={(event) => onSpeedChange(Number(event.target.value))}
          disabled={!interactive || complete}
        >
          <option value={10}>10×</option>
          <option value={20}>20×</option>
          <option value={40}>40×</option>
        </select>
      </label>
      <span className="sound-state">⊘ SOUND OFF</span>
    </div>
  );
}
