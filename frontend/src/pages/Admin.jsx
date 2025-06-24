import React, { useState } from "react";
import NavBar from "../components/NavBar";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";

function Admin() {
  const [playerPoints, setPlayerPoints] = useState([]);
  const [fetchSuccess, setFetchSuccess] = useState(false);
  const [fetchError, setFetchError] = useState(false);

  const fetchPlayerPoints = () => {
    setFetchSuccess(false); // Reset state before new request
    setFetchError(false);

    fetch("http://localhost:8000/points/")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        setPlayerPoints(data.playerPoints);
        setFetchSuccess(true);
      })
      .catch((err) => {
        console.error(err);
        setFetchError(true);
      });
  };

  return (
    <div>
      <NavBar />
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          marginY: 4,
        }}
      >
        <Button variant="contained" onClick={fetchPlayerPoints}>
          Fetch Player Points
        </Button>
      </Box>

      {fetchSuccess && (
        <Alert severity="success">Players fetched successfully</Alert>
      )}
      {fetchError && (
        <Alert severity="error">Failed to fetch player points</Alert>
      )}
    </div>
  );
}

export default Admin;
