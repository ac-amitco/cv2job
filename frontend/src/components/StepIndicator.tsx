const STEPS = ['Upload', 'Review', 'Results']

export default function StepIndicator({ active }: { active: number }) {
  return (
    <nav className="steps" aria-label="Progress">
      {STEPS.map((label, i) => (
        <span
          key={label}
          className={`step${i === active ? ' step-active' : ''}${
            i < active ? ' step-done' : ''
          }`}
        >
          <span className="step-dot">{i < active ? '✓' : i + 1}</span>
          {label}
        </span>
      ))}
    </nav>
  )
}
