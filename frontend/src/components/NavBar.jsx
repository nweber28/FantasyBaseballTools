import * as React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();

  const isAdminPage = location.pathname === "/admin";

  const handleNavigation = () => {
    navigate(isAdminPage ? "/" : "/admin");
  };
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {isAdminPage ? "Admin" : "Home"}
          </Typography>
          <Button color="inherit" onClick={handleNavigation}>
            {isAdminPage ? "Home" : "Admin"}
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
