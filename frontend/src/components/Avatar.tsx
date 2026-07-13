export default function Avatar({
  name,
  src,
  size,
}: {
  name: string;
  src?: string | null;
  size?: "sm" | "lg";
}) {
  return (
    <div className={`avatar ${size ?? ""}`}>
      {src ? <img src={src} alt={name} /> : (name || "؟").charAt(0)}
    </div>
  );
}
