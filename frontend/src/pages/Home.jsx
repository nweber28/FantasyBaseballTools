import React, { useState } from "react";
import ResponsiveTable from "../components/ResponsiveTable.jsx";

function Home() {
  const [draftPicks, setDraftPicks] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // populates draft data base, only needed to do this once
  const fetchDraftPicks = () => {
    fetch("http://localhost:8000/draft/")
      .then((res) => res.json())
      .then((data) => setDraftPicks(data.draftPicks))
      .catch((err) => console.error(err));
  };

  const calculateDraftMetrics = () => {
    fetch("http://localhost:8000/calculate-draft-metrics/", {
      method: "POST", // ← still required
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // ← optional, but helps avoid issues with some servers
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Metrics calculated:", data);
        alert(data.message || "Success");
      })
      .catch((err) => console.error("Error calculating metrics:", err));
  };

  return (
    <div>
      {/* <button onClick={calculateDraftMetrics}>Calculate Draft Metrics</button> */}
      <ResponsiveTable
        key={refreshKey}
        apiUrl="http://localhost:8000/api/playerData/"
      />

      {/* <div>
        <h1>Players</h1>
        
        {players.length > 0 && (
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Jersey</th>
                <th>Team ID</th>
                <th>Injury Status</th>
              </tr>
            </thead>
            <tbody>
              {players.map((player) => (
                <tr key={player.id}>
                  <td>{player.fullName}</td>
                  <td>{player.jersey}</td>
                  <td>{player.proTeamId}</td>
                  <td>{player.injuryStatus}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div> */}

      {/* <div>
        <h1>Draft Picks</h1>
        <button onClick={fetchDraftPicks}>Load Draft Picks</button>
        {draftPicks.length > 0 && (
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Id</th>
                <th>Keeper?</th>
                <th>Player Id</th>
                <th>Round</th>
                <th>Pick</th>
                <th>Team</th>
                <th>Pick Overall</th>
              </tr>
            </thead>
            <tbody>
              {draftPicks.map((pick) => (
                <tr key={pick.id}>
                  <td>{pick.id}</td>
                  <td>{pick.reservedForKeeper ? "Yes" : "No"}</td>
                  <td>{pick.playerId}</td>
                  <td>{pick.roundId}</td>
                  <td>{pick.roundPickNumber}</td>
                  <td>{pick.teamId}</td>
                  <td>{pick.overallPickNumber}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div> */}
    </div>
  );
}

export default Home;
