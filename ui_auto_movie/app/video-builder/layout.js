
export default function VideoBuilderLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <main>
        {children}
      </main>
    </div>
  );
}
