import { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Layout from "./components/Layout";
import { AdminDashboard, AdminLayout } from "./pages/admin/AdminHome";
import AdminAgents from "./pages/admin/AdminAgents";
import AdminInvites from "./pages/admin/AdminInvites";
import { AdminMessages, AdminPosts } from "./pages/admin/AdminModeration";
import AdminUsers from "./pages/admin/AdminUsers";
import Chat from "./pages/Chat";
import Feed from "./pages/Feed";
import InviteAccept from "./pages/InviteAccept";
import Login from "./pages/Login";
import Messages from "./pages/Messages";
import Notifications from "./pages/Notifications";
import People from "./pages/People";
import Profile from "./pages/Profile";
import { ThemeProvider } from "./theme";

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="spinner" />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RequireAdmin({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="spinner" />;
  if (!user?.is_staff) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/invite/:token" element={<InviteAccept />} />
            <Route
              element={
                <RequireAuth>
                  <Layout />
                </RequireAuth>
              }
            >
              <Route path="/" element={<Feed />} />
              <Route path="/people" element={<People />} />
              <Route path="/profile/:id" element={<Profile />} />
              <Route path="/messages" element={<Messages />} />
              <Route path="/messages/:id" element={<Chat />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route
                path="/admin"
                element={
                  <RequireAdmin>
                    <AdminLayout />
                  </RequireAdmin>
                }
              >
                <Route index element={<AdminDashboard />} />
                <Route path="users" element={<AdminUsers />} />
                <Route path="invites" element={<AdminInvites />} />
                <Route path="posts" element={<AdminPosts />} />
                <Route path="messages" element={<AdminMessages />} />
                <Route path="agents" element={<AdminAgents />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
