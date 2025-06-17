import React, { useState } from "react";

function Admin() {
  const [playerPoints, setPlayerPoints] = useState([]);
  const fetchPlayerPoints = () => {
    fetch("http://localhost:8000/points/")
      .then((res) => res.json())
      .then((data) => {
        setPlayerPoints(data.playerPoints);
        //setRefreshKey((prevKey) => prevKey + 1);
      })
      .catch((err) => console.error(err));
  };

  return (
    <div>
      Admin Page
      <div>
        <h1>Player Points 2025</h1>
        <button onClick={fetchPlayerPoints}>Load Player Points</button>

        {playerPoints.length > 0 &&
          playerPoints.map((team) => (
            <div key={team.teamId} style={{ marginBottom: "2rem" }}>
              <h2>Team {team.teamId}</h2>
              <table border="1" cellPadding="5">
                <thead>
                  <tr>
                    <th>Player ID</th>
                    <th>Player Name</th>
                    <th>Points Scored</th>
                  </tr>
                </thead>
                <tbody>
                  {team.players.map((player) => (
                    <tr key={player.id}>
                      <td>{player.id}</td>
                      <td>{player.fullName}</td>
                      <td>{player.points ?? "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
      </div>
    </div>
  );
}

export default Admin;
