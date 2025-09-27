
const st = "hello world";

function strinttoCapitalize(str) {

    const words = str.split(" ")

    return words.map(word => word.charAt(0).toUpperCase() + word.slice(1));
}

const res = strinttoCapitalize(st);

console.log(res);