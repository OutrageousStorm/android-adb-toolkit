const net = require("net");

class PacketAnalyzer {
  constructor() {
    this.packets = [];
  }

  analyze(data) {
    this.packets.push({
      time: new Date().toISOString(),
      size: data.length,
      hex: data.toString("hex").substring(0, 64)
    });
    console.log(`[+] ${data.length} bytes`);
  }

  stats() {
    const total = this.packets.reduce((s, p) => s + p.size, 0);
    return {
      count: this.packets.length,
      bytes: total,
      avg: Math.round(total / this.packets.length)
    };
  }
}

module.exports = PacketAnalyzer;
