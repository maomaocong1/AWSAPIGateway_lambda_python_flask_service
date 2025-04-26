const { fromPath } = require('pdf2pic');
const Jimp = require('jimp').default;
const jsQR = require('jsqr');
const fs = require('fs');

async function convertAllPagesFromPDF(pdfPath, outputDir) {
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const options = {
        density: 300,               // Quality
        savePath: outputDir,
        format: "png",              // Or "jpeg"
        width: 1000,
        height: 1400
    };

    const convert = fromPath(pdfPath, options);

    try {
        const result = await convert.bulk(-1); // -1 means ALL pages
        console.log(`Successfully converted ${result.length} pages!`);
        return result.map(r => r.path); // return paths to all generated images
    } catch (error) {
        console.error("PDF conversion error:", error);
        throw error;
    }
}

async function pdfFirstPageQrScan(pdfPath) {
    const options = {
        density: 300,
        saveFilename: "page",
        savePath: "./",
        format: "png",
        width: 800,
        height: 1000
    };

    const convert = fromPath(pdfPath, options);

    try {
        const resolve = await convert(1); // Only page 1
        console.log("First page converted:", resolve);

        const image = await Jimp.read(resolve.path);
        const { data, width, height } = image.bitmap;

        const qrCode = jsQR(new Uint8ClampedArray(data), width, height);

        if (qrCode) {
            console.log("QR Code Found:", qrCode.data);
            return qrCode.data;
        } else {
            console.log("No QR Code found.");
            return null;
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Usage
pdfFirstPageQrScan("Doc0035.pdf");


// // Example Usage:
// (async () => {
//     const pdfPath = "./Doc0035.pdf";
//     const outputDir = "./";
//     const imagePaths = await convertAllPagesFromPDF(pdfPath, outputDir);

//     console.log("All images generated:", imagePaths);
// })();
