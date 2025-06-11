import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useEffect } from "react";

function ProtectedRoute({ children }) {
  // check if authorized before accessing route
  const [isAuthorized, setIsAuthorized] = useState(null);

  // refresh access token automatically
  const refreshToken = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN);

    // when protected route is loaded call auth
    useEffect(() => {
      auth().catch(() => setIsAuthorized(false));
    }, []);

    try {
      // send to backend for new backend token
      const res = await api.post("/api/token/refresh/", {
        refresh: refreshToken,
      });

      if (res.status === 200) {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    } catch (error) {
      console.log(error);
      setIsAuthorized(false);
    }
  };

  // check if token needs refresh
  const auth = async () => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) {
      setIsAuthorized(false);
      return;
    }
    const decoded = jwtDecode(token);
    const tokenExpiration = decoded.exp;
    const now = Date.now() / 1000; // date in seconds

    if (tokenExpiration < now) {
      // token is expired
      await refreshToken();
    } else {
      setIsAuthorized(true);
    }
  };

  if (isAuthorized == null) {
    return <div>Loading...</div>;
  }

  return isAuthorized ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
