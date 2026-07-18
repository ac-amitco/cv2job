interface Props {
  message: string
  detail?: string
}

export default function LoadingState({ message, detail }: Props) {
  return (
    <section className="loading-state" role="status">
      <div className="spinner" aria-hidden />
      <p className="loading-message">{message}</p>
      {detail && <p className="loading-detail">{detail}</p>}
    </section>
  )
}
